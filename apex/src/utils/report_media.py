import html
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd
from newspaper import Article, Config
from openai import OpenAI
from openai import APIConnectionError, APITimeoutError, RateLimitError
from src.config import get_settings


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
    article_download_timeout_seconds: int = 30
    openai_timeout_seconds: int = 60


class ReportGenerationError(RuntimeError):
    pass


def friendly_report_error(exc: Exception) -> str:
    message = str(exc)

    if isinstance(exc, ReportGenerationError):
        return message
    if isinstance(exc, (APITimeoutError, APIConnectionError)):
        return "A OpenAI demorou para responder ou ficou indisponível temporariamente. Tente gerar o relatório novamente."
    if isinstance(exc, RateLimitError) or "rate limit" in message.lower() or "quota" in message.lower():
        return "A chave OpenAI atingiu limite ou cota. Verifique seu plano e tente novamente."
    if "timed out" in message.lower() or "timeout" in message.lower():
        return "Uma integracao externa demorou para responder. Tente novamente em instantes."

    return "Não foi possível gerar o relatório agora. Tente novamente ou revise as credenciais configuradas."


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
        report_options: Optional[dict[str, Any]] = None,
        config: Optional[MonitoringConfig] = None,
    ) -> None:
        self.tokenizer = tokenizer
        self.articles = articles
        self.report_options = report_options or {}
        self.config = config or MonitoringConfig()
        settings = get_settings()
        self.config.article_download_timeout_seconds = settings.external_request_timeout_seconds
        self.config.openai_timeout_seconds = settings.openai_timeout_seconds

        self.client = OpenAI(api_key=openai_api_key, timeout=self.config.openai_timeout_seconds)

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
        article_config = Config()
        article_config.request_timeout = self.config.article_download_timeout_seconds
        article = Article(url, config=article_config)

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
Analise este artigo de notícias como analista de comunicação estratégica e responda apenas em JSON válido.

Use exatamente estas chaves:
- "Temas principais"
- "Resumo"
- "Narrativas"
- "Opiniões"
- "Porta-vozes"
- "Viés"
- "Emoção do artigo"
- "Risco"
- "Oportunidade"
- "Relevância"

Regras:
- Seja claro e conciso.
- Não adicione texto fora do JSON.
- Caso alguma informação não exista, retorne uma string vazia.
- Separe fatos observáveis de inferências.
- A chave "Relevância" deve ser uma nota de 1 a 5 explicada em uma frase.

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

        content = self.strip_json_fence(content)
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return {str(key): str(value) for key, value in parsed.items()}
        except json.JSONDecodeError:
            logger.warning("Model response is not valid JSON. Trying fallback parser.")

        return self.fallback_parse_response(content)

    def strip_json_fence(self, content: str) -> str:
        content = (content or "").strip()
        if content.startswith("```"):
            lines = content.splitlines()
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines).strip()
        return content

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
                df.loc[index, "risk"] = parsed_data.get("Risco", "")
                df.loc[index, "opportunity"] = parsed_data.get("Oportunidade", "")
                df.loc[index, "relevance"] = parsed_data.get("Relevância", "")

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
        article_rows: list[dict[str, str]],
    ) -> str:
        audience = self.report_options.get("audience") or "cliente executivo"
        objective = self.report_options.get("objective") or "entender o cenário de mídia e orientar próximos passos"
        tone = self.report_options.get("tone") or "executivo"
        report_type = self.report_options.get("report_type") or "monitoramento"
        return f"""
Gere um relatório de monitoramento de mídia em JSON válido para ser renderizado por uma aplicação.

Contexto:
- Tipo de relatório: {report_type}
- Público-alvo: {audience}
- Objetivo: {objective}
- Tom: {tone}

Informações mais comuns:
{most_common}

Porta-vozes mais frequentemente mencionados:
{spokesperson_counts}

Artigos ou fontes mais tendenciosos:
{bias_counts}

Artigos analisados:
{json.dumps(article_rows, ensure_ascii=False)}

Responda apenas um JSON com estas chaves:
- "executive_summary": lista com 3 a 5 frases objetivas.
- "context": string curta explicando a busca.
- "key_findings": lista de objetos com "title", "evidence" e "impact".
- "sentiment": string com leitura geral do sentimento.
- "risks": lista de objetos com "risk", "evidence" e "mitigation".
- "opportunities": lista de objetos com "opportunity", "evidence" e "action".
- "recommendations": lista de objetos com "action", "reason" e "priority".
- "methodology": string curta explicando que a análise se limita às fontes selecionadas.

Regras:
- Cite somente fatos presentes nos artigos analisados.
- Separe fatos de inferências.
- Se houver poucos dados, sinalize baixa confiança.
- Não invente porta-vozes, datas ou fatos.
""".strip()

    def generate_report(
        self,
        most_common: dict[str, int],
        spokesperson_counts: dict[str, int],
        bias_counts: dict[str, int],
        article_rows: list[dict[str, str]],
    ) -> str:
        """
        Gera o relatório consolidado com base nas análises dos artigos.
        """
        prompt = self.build_report_prompt(
            most_common=most_common,
            spokesperson_counts=spokesperson_counts,
            bias_counts=bias_counts,
            article_rows=article_rows,
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

    def parse_report_response(self, content: str) -> dict[str, Any]:
        content = self.strip_json_fence(content)
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            logger.warning("Report response is not valid JSON. Using fallback report.")

        return {
            "executive_summary": [content.strip() or "Não foi possível estruturar o resumo executivo."],
            "context": "",
            "key_findings": [],
            "sentiment": "",
            "risks": [],
            "opportunities": [],
            "recommendations": [],
            "methodology": "Análise limitada às fontes selecionadas pelo usuário.",
        }

    def render_dict_item(self, item: dict[str, Any], section_key: str) -> str:
        section_fields = {
            "key_findings": (
                ("title", "tema"),
                "Achado relevante",
                ("evidence", "evidencia"),
                ("impact", "impacto"),
            ),
            "risks": (
                ("risk", "risco", "title", "tema"),
                "Risco identificado",
                ("evidence", "evidencia"),
                ("mitigation", "mitigacao", "mitigação", "impact", "impacto"),
            ),
            "opportunities": (
                ("opportunity", "oportunidade", "title", "tema"),
                "Oportunidade identificada",
                ("evidence", "evidencia"),
                ("action", "acao", "ação", "impact", "impacto"),
            ),
            "recommendations": (
                ("action", "acao", "ação", "recommendation", "recomendacao", "recomendação", "title"),
                "Recomendação prática",
                ("reason", "justificativa", "rationale", "evidence", "evidencia"),
                ("priority", "prioridade", "impact", "impacto"),
            ),
        }
        title_keys, fallback_title, detail_keys, note_keys = section_fields.get(
            section_key,
            (("title", "tema"), "", ("description", "descricao", "descrição"), ("impact", "impacto")),
        )

        def first_value(keys):
            for key in keys:
                value = item.get(key)
                if value:
                    return str(value)
            return ""

        title = first_value(title_keys)
        detail = first_value(detail_keys)
        note = first_value(note_keys)

        if not title and not detail and not note:
            values = [str(value) for value in item.values() if value]
            detail = " ".join(values)

        title_html = f"<strong>{html.escape(title or fallback_title)}</strong><br>" if title or fallback_title else ""
        detail_html = f"{html.escape(detail)}<br>" if detail else ""
        note_html = f"<em>{html.escape(note)}</em>" if note else ""
        return f"<li>{title_html}{detail_html}{note_html}</li>"

    def render_list(self, items: Any, section_key: str = "") -> str:
        if not items:
            return "<p>Sem apontamentos suficientes nas fontes selecionadas.</p>"
        if not isinstance(items, list):
            items = [items]

        rendered = []
        for item in items:
            if isinstance(item, dict):
                rendered.append(self.render_dict_item(item, section_key))
            else:
                rendered.append(f"<li>{html.escape(str(item))}</li>")
        return "<ul>" + "".join(rendered) + "</ul>"

    def render_report_html(self, report_data: dict[str, Any], article_rows: list[dict[str, str]]) -> str:
        title = html.escape(str(self.report_options.get("title") or "Relatório de Monitoramento"))
        objective = html.escape(str(self.report_options.get("objective") or ""))
        audience = html.escape(str(self.report_options.get("audience") or ""))

        sources = "".join(
            (
                "<li>"
                f"<strong>{html.escape(row.get('title', ''))}</strong>"
                f" - {html.escape(row.get('source', ''))}"
                f"<br><a href=\"{html.escape(row.get('link', ''))}\" target=\"_blank\" rel=\"noreferrer\">Abrir fonte</a>"
                "</li>"
            )
            for row in article_rows
        )

        return f"""
<article class="apex-generated-report">
  <header>
    <p class="eyebrow">APEX | Monitoramento de mídia</p>
    <h1>{title}</h1>
    <p><strong>Público-alvo:</strong> {audience or "Não informado"}</p>
    <p><strong>Objetivo:</strong> {objective or "Não informado"}</p>
  </header>
  <section>
    <h2>Resumo executivo</h2>
    {self.render_list(report_data.get("executive_summary"), "executive_summary")}
  </section>
  <section>
    <h2>Contexto</h2>
    <p>{html.escape(str(report_data.get("context") or "Análise baseada nos conteúdos selecionados pelo usuário."))}</p>
  </section>
  <section>
    <h2>Principais achados</h2>
    {self.render_list(report_data.get("key_findings"), "key_findings")}
  </section>
  <section>
    <h2>Sentimento e leitura estratégica</h2>
    <p>{html.escape(str(report_data.get("sentiment") or "Sem dados suficientes para uma leitura consolidada."))}</p>
  </section>
  <section>
    <h2>Riscos</h2>
    {self.render_list(report_data.get("risks"), "risks")}
  </section>
  <section>
    <h2>Oportunidades</h2>
    {self.render_list(report_data.get("opportunities"), "opportunities")}
  </section>
  <section>
    <h2>Recomendações</h2>
    {self.render_list(report_data.get("recommendations"), "recommendations")}
  </section>
  <section>
    <h2>Fontes analisadas</h2>
    <ul>{sources}</ul>
  </section>
  <footer>
    <h2>Observações metodológicas</h2>
    <p>{html.escape(str(report_data.get("methodology") or "A análise se limita às fontes selecionadas e ao conteúdo disponível no momento da geração."))}</p>
  </footer>
</article>
""".strip()

    def analyze_dataframe(self) -> str:
        """
        Gera o HTML final com:
        - Resumo de cada artigo
        - Fonte
        - Relatório consolidado
        """
        if self.df.empty:
            raise ReportGenerationError(
                "Resultado incompleto, falha na integração com GPT. "
                "Entre em contato com o suporte para ajustar."
            )

        df = self.df.drop_duplicates().copy()

        if "main_themes" not in df.columns:
            if self.error:
                raise ReportGenerationError(self.error)

            raise ReportGenerationError("Nenhuma análise foi gerada para os artigos.")

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

        article_rows = []
        for _, row in df.iterrows():
            article_rows.append(
                {
                    "title": str(row.get("title", "")),
                    "source": str(row.get("source", "")),
                    "link": str(row.get("link", "")),
                    "summary": str(row.get("resume", "")),
                    "themes": str(row.get("main_themes", "")),
                    "risk": str(row.get("risk", "")),
                    "opportunity": str(row.get("opportunity", "")),
                    "relevance": str(row.get("relevance", "")),
                }
            )

        report = self.generate_report(
            most_common=most_common,
            spokesperson_counts=spokesperson_counts,
            bias_counts=bias_counts,
            article_rows=article_rows,
        )
        report_data = self.parse_report_response(report)

        report_html = self.render_report_html(report_data, article_rows)

        return {
            "version": 2,
            "data": report_data,
            "html": report_html,
            "legacy_html": "".join(html_parts),
            "articles": article_rows,
            "options": self.report_options,
        }
