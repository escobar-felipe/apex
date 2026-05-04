import html
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd
from newspaper import Article
from openai import OpenAI


logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    analysis_model: str = "gpt-5-mini"
    report_model: str = "gpt-5-mini"
    max_input_chars: int = 14500
    max_article_tokens: int = 18000
    max_output_tokens: int = 18000
    request_delay_seconds: float = 2.0
    temperature: float = 0.5


class MonitoringAndAnalysis:
    """
    Classe responsável por:
    - Baixar textos de artigos usando newspaper3k
    - Analisar os artigos com OpenAI
    - Salvar os resultados em um DataFrame
    - Gerar um relatório HTML consolidado
    """

    ANALYSIS_COLUMNS = {
        "main_themes": "Temas principais",
        "resume": "Resumo",
        "narratives": "Narrativas",
        "opinions": "Opiniões",
        "spokespersons": "Porta-vozes",
        "biases": "Viés",
        "emotion": "Emoção do artigo",
    }

    DEFAULT_RESUME_ERROR = (
        "Nossa Inteligência Artificial não conseguiu gerar um resumo para esse artigo."
    )

    def __init__(
        self,
        tokenizer: Any,
        articles: list[dict[str, Any]],
        openai_api_key: str,
        config: Optional[MonitoringConfig] = None,
    ) -> None:
        self.tokenizer = tokenizer
        self.articles = articles
        self.config = config or MonitoringConfig()

        self.client = OpenAI(api_key=openai_api_key)

        self.df = pd.DataFrame()
        self.error: Optional[str] = None

    def truncate_text(self, text: str, max_tokens: Optional[int] = None) -> str:
        """
        Limita o texto usando o tokenizer informado.
        Mantém o corte inicial por caracteres para evitar textos muito grandes.
        """
        if not text:
            return ""

        max_tokens = max_tokens or self.config.max_article_tokens

        text = text[: self.config.max_input_chars]
        token_ids = self.tokenizer.encode(text)

        if len(token_ids) > max_tokens:
            token_ids = token_ids[:max_tokens]

        return self.tokenizer.decode(token_ids)

    def scrape_article(self, url: str) -> str:
        """
        Baixa e extrai o conteúdo textual de uma URL.
        Retorna título + texto.
        """
        article = Article(url)

        try:
            article.download()
            article.parse()

            logger.info("Article downloaded successfully: %s", article.title)

            return f"{article.title or ''} {article.text or ''}".strip()

        except Exception as exc:
            logger.exception("Failed to download article: %s", url)
            self.error = str(exc)
            return ""

    def fetch_articles(self, articles: Optional[list[dict[str, Any]]] = None) -> pd.DataFrame:
        """
        Converte a lista de artigos em DataFrame e adiciona o texto extraído.
        """
        articles = articles or self.articles
        rows: list[dict[str, Any]] = []

        for article in articles:
            rows.append(
                {
                    "brand": article.get("brand", ""),
                    "title": article.get("title", ""),
                    "link": article.get("link", ""),
                    "source": article.get("source", ""),
                    "text": self.scrape_article(article.get("link", "")),
                }
            )

        return pd.DataFrame(rows)

    def build_analysis_prompt(self, article_text: str) -> str:
        """
        Cria o prompt de análise e pede JSON para facilitar o parsing.
        """
        return f"""
Analise este artigo de notícias e responda apenas em JSON válido.

Use exatamente estas chaves:
- "Temas principais"
- "Resumo"
- "Narrativas"
- "Opiniões"
- "Porta-vozes"
- "Viés"
- "Emoção do artigo"

Regras:
- Seja claro e conciso.
- Não adicione texto fora do JSON.
- Caso alguma informação não exista, retorne uma string vazia.

Artigo:
{article_text}
""".strip()

    def parse_analysis_response(self, content: str) -> dict[str, str]:
        """
        Faz parsing da resposta do modelo.
        Se o JSON vier malformado, tenta retornar um fallback seguro.
        """
        if not content:
            return {}

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return {str(key): str(value) for key, value in parsed.items()}
        except json.JSONDecodeError:
            logger.warning("Model response is not valid JSON. Trying fallback parser.")

        return self.fallback_parse_response(content)

    def fallback_parse_response(self, content: str) -> dict[str, str]:
        """
        Parser alternativo para respostas no formato:
        Chave: valor
        """
        parsed_data: dict[str, str] = {}

        for line in content.splitlines():
            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if key:
                parsed_data[key] = value

        return parsed_data

    def analyze_single_article(self, article_text: str) -> dict[str, str]:
        """
        Envia um artigo para análise no modelo.
        """
        truncated_text = self.truncate_text(article_text)
        prompt = self.build_analysis_prompt(truncated_text)

        response = self.client.chat.completions.create(
            model=self.config.analysis_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em análise de mídia, "
                        "relações públicas, psicologia e comportamento humano."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=self.config.max_output_tokens,
            # temperature=self.config.temperature,
        )

        content = response.choices[0].message.content or ""
        return self.parse_analysis_response(content.strip())

    def analyze_articles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analisa os artigos do DataFrame e adiciona as colunas de resultado.
        """
        if df.empty:
            return df

        df = df.copy()

        for index, row in df.iterrows():
            try:
                if self.config.request_delay_seconds:
                    time.sleep(self.config.request_delay_seconds)

                article_text = row.get("text", "")
                parsed_data = self.analyze_single_article(article_text)

                df.loc[index, "main_themes"] = parsed_data.get("Temas principais", "")
                df.loc[index, "resume"] = parsed_data.get(
                    "Resumo",
                    self.DEFAULT_RESUME_ERROR,
                )
                df.loc[index, "narratives"] = parsed_data.get("Narrativas", "")
                df.loc[index, "opinions"] = parsed_data.get("Opiniões", "")
                df.loc[index, "spokespersons"] = parsed_data.get("Porta-vozes", "")
                df.loc[index, "biases"] = parsed_data.get("Viés", "")
                df.loc[index, "emotion"] = parsed_data.get("Emoção do artigo", "")

            except Exception as exc:
                logger.exception("Failed to analyze article at index %s", index)
                self.error = str(exc)

                df.loc[index, "resume"] = self.DEFAULT_RESUME_ERROR

        return df

    def get_analyze_from_articles(self) -> pd.DataFrame:
        """
        Executa o fluxo completo:
        1. Busca os artigos
        2. Analisa os artigos
        3. Retorna o DataFrame final
        """
        self.df = self.fetch_articles(self.articles)
        self.df = self.analyze_articles(self.df)

        return self.df

    def build_report_prompt(
        self,
        most_common: dict[str, int],
        spokesperson_counts: dict[str, int],
        bias_counts: dict[str, int],
    ) -> str:
        return f"""
Gere um relatório de monitoramento de mídia com base nos dados abaixo.

Informações mais comuns:
{most_common}

Porta-vozes mais frequentemente mencionados:
{spokesperson_counts}

Artigos ou fontes mais tendenciosos:
{bias_counts}

Escreva um relatório bem estruturado e conciso resumindo as principais descobertas.
""".strip()

    def generate_report(
        self,
        most_common: dict[str, int],
        spokesperson_counts: dict[str, int],
        bias_counts: dict[str, int],
    ) -> str:
        """
        Gera o relatório consolidado com base nas análises dos artigos.
        """
        prompt = self.build_report_prompt(
            most_common=most_common,
            spokesperson_counts=spokesperson_counts,
            bias_counts=bias_counts,
        )

        response = self.client.chat.completions.create(
            model=self.config.report_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em análise de mídia, "
                        "psicologia, comportamento humano e relações públicas."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=4024,
            # temperature=self.config.temperature,
        )

        return (response.choices[0].message.content or "").strip()

    def analyze_dataframe(self) -> str:
        """
        Gera o HTML final com:
        - Resumo de cada artigo
        - Fonte
        - Relatório consolidado
        """
        if self.df.empty:
            raise Exception(
                "Resultado incompleto, falha na integração com GPT. "
                "Entre em contato com o suporte para ajustar."
            )

        df = self.df.drop_duplicates().copy()

        if "main_themes" not in df.columns:
            if self.error:
                raise Exception(self.error)

            raise Exception("Nenhuma análise foi gerada para os artigos.")

        most_common = df["main_themes"].value_counts().head(5).to_dict()
        spokesperson_counts = df["spokespersons"].value_counts().head(5).to_dict()
        bias_counts = df["biases"].value_counts().head(5).to_dict()

        html_parts: list[str] = []

        for _, row in df.iterrows():
            title = html.escape(str(row.get("title", "")))
            source = html.escape(str(row.get("source", "")))

            resume = row.get("resume")
            if pd.isna(resume) or not str(resume).strip():
                resume = self.DEFAULT_RESUME_ERROR

            resume = html.escape(str(resume))

            html_parts.append(f"<h3>{title}</h3>")
            html_parts.append(
                '<p style="font-size:16px;margin:0 0 20px 0;font-family:Arial,sans-serif;">'
                f"{resume}"
                "</p>"
            )
            html_parts.append(
                '<p style="font-size:16px;margin:0 0 20px 0;font-family:Arial,sans-serif;">'
                f"Fonte: {source}"
                "</p>"
            )
            html_parts.append("<br>")

        report = self.generate_report(
            most_common=most_common,
            spokesperson_counts=spokesperson_counts,
            bias_counts=bias_counts,
        )

        html_parts.append("<h3>Análise</h3><br>")
        html_parts.append(
            '<p style="font-size:16px;margin:0 0 20px 0;font-family:Arial,sans-serif;">'
            f"{html.escape(report)}"
            "</p>"
        )

        return "".join(html_parts)