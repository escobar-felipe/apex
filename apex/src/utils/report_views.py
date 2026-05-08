import html as html_lib
from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from src.utils.report_html import sanitize_report_html


SECTION_LABELS = {
    "executive_summary": "Resumo executivo",
    "context": "Contexto",
    "key_findings": "Principais achados",
    "sentiment": "Sentimento e leitura estratégica",
    "risks": "Riscos",
    "opportunities": "Oportunidades",
    "recommendations": "Recomendações",
    "methodology": "Observações metodológicas",
}


def get_report_html(payload):
    if isinstance(payload, dict):
        if payload.get("data"):
            return sanitize_report_html(render_report_html_from_data(payload))
        return sanitize_report_html(payload.get("html") or payload.get("legacy_html") or "")
    return sanitize_report_html(payload)


def get_report_data(payload):
    if isinstance(payload, dict):
        return payload.get("data") or {}
    return {}


SECTION_FIELDS = {
    "key_findings": {
        "title": ("title", "tema"),
        "fallback": "Achado relevante",
        "detail": ("evidence", "evidencia"),
        "note": ("impact", "impacto"),
    },
    "risks": {
        "title": ("risk", "risco", "title", "tema"),
        "fallback": "Risco identificado",
        "detail": ("evidence", "evidencia"),
        "note": ("mitigation", "mitigacao", "mitigação", "impact", "impacto"),
    },
    "opportunities": {
        "title": ("opportunity", "oportunidade", "title", "tema"),
        "fallback": "Oportunidade identificada",
        "detail": ("evidence", "evidencia"),
        "note": ("action", "acao", "ação", "impact", "impacto"),
    },
    "recommendations": {
        "title": ("action", "acao", "ação", "recommendation", "recomendacao", "recomendação", "title"),
        "fallback": "Recomendação prática",
        "detail": ("reason", "justificativa", "rationale", "evidence", "evidencia"),
        "note": ("priority", "prioridade", "impact", "impacto"),
    },
}


def first_dict_value(item, keys):
    for key in keys:
        value = item.get(key)
        if value:
            return str(value)
    return ""


def render_dict_value(item, section_key):
    fields = SECTION_FIELDS.get(
        section_key,
        {
            "title": ("title", "tema"),
            "fallback": "",
            "detail": ("description", "descricao", "descrição"),
            "note": ("impact", "impacto"),
        },
    )
    title = first_dict_value(item, fields["title"])
    detail = first_dict_value(item, fields["detail"])
    note = first_dict_value(item, fields["note"])

    if not title and not detail and not note:
        detail = " ".join(str(value) for value in item.values() if value)

    children = []
    if title or fields["fallback"]:
        children.append(dmc.Text(title or fields["fallback"], weight=700))
    if detail:
        children.append(dmc.Text(detail, color="dimmed", size="sm"))
    if note:
        children.append(dmc.Text(note, color="dimmed", size="sm", italic=True))

    return children or [dmc.Text("Sem detalhe informado.", color="dimmed", size="sm")]


def render_dict_html(item, section_key):
    fields = SECTION_FIELDS.get(
        section_key,
        {
            "title": ("title", "tema"),
            "fallback": "",
            "detail": ("description", "descricao", "descrição"),
            "note": ("impact", "impacto"),
        },
    )
    title = first_dict_value(item, fields["title"])
    detail = first_dict_value(item, fields["detail"])
    note = first_dict_value(item, fields["note"])

    if not title and not detail and not note:
        detail = " ".join(str(value) for value in item.values() if value)

    title_html = f"<strong>{html_lib.escape(title or fields['fallback'])}</strong><br>" if title or fields["fallback"] else ""
    detail_html = f"{html_lib.escape(detail)}<br>" if detail else ""
    note_html = f"<em>{html_lib.escape(note)}</em>" if note else ""
    return f"<li>{title_html}{detail_html}{note_html}</li>"


def render_html_list(value, section_key):
    if not value:
        return "<p>Sem dados suficientes nas fontes selecionadas.</p>"
    if not isinstance(value, list):
        value = [value]

    items = []
    for item in value:
        if isinstance(item, dict):
            items.append(render_dict_html(item, section_key))
        else:
            items.append(f"<li>{html_lib.escape(str(item))}</li>")
    return "<ul>" + "".join(items) + "</ul>"


def render_report_html_from_data(payload):
    data = payload.get("data") or {}
    options = payload.get("options") or {}
    articles = payload.get("articles") or []
    title = html_lib.escape(str(options.get("title") or "Relatório de Monitoramento"))
    audience = html_lib.escape(str(options.get("audience") or "Não informado"))
    objective = html_lib.escape(str(options.get("objective") or "Não informado"))
    sources = "".join(
        (
            "<li>"
            f"<strong>{html_lib.escape(str(article.get('title', '')))}</strong>"
            f" - {html_lib.escape(str(article.get('source', '')))}"
            f"<br><a href=\"{html_lib.escape(str(article.get('link', '')))}\" target=\"_blank\" rel=\"noreferrer\">Abrir fonte</a>"
            "</li>"
        )
        for article in articles
    )
    return f"""
<article class="apex-generated-report">
  <header>
    <p class="eyebrow">APEX | Monitoramento de mídia</p>
    <h1>{title}</h1>
    <p><strong>Público-alvo:</strong> {audience}</p>
    <p><strong>Objetivo:</strong> {objective}</p>
  </header>
  <section><h2>Resumo executivo</h2>{render_html_list(data.get("executive_summary"), "executive_summary")}</section>
  <section><h2>Contexto</h2><p>{html_lib.escape(str(data.get("context") or "Análise baseada nos conteúdos selecionados pelo usuário."))}</p></section>
  <section><h2>Principais achados</h2>{render_html_list(data.get("key_findings"), "key_findings")}</section>
  <section><h2>Sentimento e leitura estratégica</h2><p>{html_lib.escape(str(data.get("sentiment") or "Sem dados suficientes para uma leitura consolidada."))}</p></section>
  <section><h2>Riscos</h2>{render_html_list(data.get("risks"), "risks")}</section>
  <section><h2>Oportunidades</h2>{render_html_list(data.get("opportunities"), "opportunities")}</section>
  <section><h2>Recomendações</h2>{render_html_list(data.get("recommendations"), "recommendations")}</section>
  <section><h2>Fontes analisadas</h2><ul>{sources}</ul></section>
  <footer><h2>Observações metodológicas</h2><p>{html_lib.escape(str(data.get("methodology") or "A análise se limita às fontes selecionadas e ao conteúdo disponível no momento da geração."))}</p></footer>
</article>
""".strip()


def render_value(value, section_key=""):
    if not value:
        return dmc.Text("Sem dados suficientes nas fontes selecionadas.", color="dimmed")
    if isinstance(value, list):
        children = []
        for item in value:
            if isinstance(item, dict):
                children.append(dmc.ListItem(render_dict_value(item, section_key)))
            else:
                children.append(dmc.ListItem(str(item)))
        return dmc.List(children, spacing="sm", withPadding=True)
    return dmc.Text(str(value), color="dimmed")


def report_review_components(payload):
    data = get_report_data(payload)
    if not data:
        return None

    sections = []
    for key, label in SECTION_LABELS.items():
        sections.append(
            html.Section(
                [
                    dmc.Title(label, order=3, className="apex-report-section-title"),
                    render_value(data.get(key), key),
                ],
                className="apex-report-review-section",
            )
        )
    return html.Div(sections, className="apex-report-review")


def report_email_controls(task_id, title):
    subject = f"[APEX] Relatório de monitoramento - {title or 'análise'}"
    message = (
        "Olá,\n\n"
        "Segue o relatório de monitoramento preparado pela Apex. "
        "O material reúne os principais achados, riscos, oportunidades e recomendações a partir das fontes analisadas.\n\n"
        "Fico à disposição para comentar os próximos passos."
    )
    return dmc.Stack(
        [
            dmc.Group(
                [
                    dmc.TextInput(
                        id={"type": "input_email", "index": task_id},
                        label="Destinatário",
                        placeholder="cliente@empresa.com",
                        style={"width": 280},
                    ),
                    dmc.TextInput(
                        id={"type": "input_email_subject", "index": task_id},
                        label="Assunto",
                        value=subject,
                        style={"flex": 1, "minWidth": 280},
                    ),
                ],
                className="apex-actions-row",
            ),
            dmc.Textarea(
                id={"type": "input_email_message", "index": task_id},
                label="Mensagem de acompanhamento",
                value=message,
                autosize=True,
                minRows=4,
            ),
            dmc.LoadingOverlay(
                dmc.Button(
                    "Enviar ao cliente",
                    id={"type": "button_send", "index": task_id},
                    n_clicks=0,
                    className="apex-button",
                    color="#504cab",
                    leftIcon=DashIconify(icon="mdi:send-outline", width=20),
                ),
                loaderProps={"variant": "oval", "color": "#504cab", "size": "sm"},
            ),
        ],
        spacing="sm",
        className="mb-3",
    )
