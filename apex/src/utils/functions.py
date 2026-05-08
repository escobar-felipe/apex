import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash import html
from dash_iconify import DashIconify
import requests
from requests import RequestException
from flask_login import current_user
import json
from src.config import get_settings


class SearchProviderError(RuntimeError):
    pass


def _serper_post(path, payload):
    if not current_user.serpapi_key:
        raise SearchProviderError("Cadastre uma chave SerperAPI para realizar pesquisas.")

    url = f"https://google.serper.dev/{path}"
    settings = get_settings()
    headers = {
        'X-API-KEY': current_user.serpapi_key,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=settings.external_request_timeout_seconds)
    except RequestException:
        raise SearchProviderError("Não foi possível conectar a SerperAPI. Tente novamente em instantes.")

    try:
        data = response.json()
    except ValueError:
        raise SearchProviderError("A SerperAPI retornou uma resposta invalida.")

    if response.status_code in {401, 403}:
        raise SearchProviderError("Chave SerperAPI inválida ou não autorizada.")
    if response.status_code == 429:
        raise SearchProviderError("Limite da SerperAPI atingido. Tente novamente mais tarde.")
    if response.status_code >= 400:
        message = data.get("message") or "Erro ao consultar a SerperAPI."
        raise SearchProviderError(message)

    return data


def validate_serper_api():
    _serper_post(
        "search",
        {
            "q": "apex",
            "gl": "br",
            "hl": "pt-br",
            "num": 1,
        },
    )


def normalize_search_result(result):
    title = result.get("title") or "Título não informado"
    link = result.get("link") or "#"
    snippet = result.get("snippet") or result.get("description") or "Descrição não informada"
    source = result.get("source") or result.get("domain") or "Fonte não identificada"
    date = result.get("date") or "Data não informada"

    return {
        "title": str(title),
        "link": str(link),
        "description": f"{date} - {snippet}",
        "source": str(source),
    }


def _limited_results(results, limit):
    return results[:limit]


def shorten_string(s):
    if len(s) > 27:
        return s[:24] + "..."
    else:
        return s
    

def add_zero(s):
    if s < 10:
        return "0"+ str(s)
    else:
        return str(s)
    


class Card():
    def __init__(self,title,body, source, link) -> None:  
        self.title = title
        self.body = body
        self.source = source
        self.link = link
        super().__init__()


def create_cards(cards_list:Card):
    card_append =dbc.Card(
                dbc.CardBody(
                    [
                        html.H5(cards_list.title, className="card-title"),
                        html.P(cards_list.body, className="mb-3"),
                        dmc.Group([
                            html.P(dmc.Text(["fonte: " +cards_list.source], weight=700, color="gray",className="mb-2")),
                            html.A(dmc.Text([DashIconify(icon="ic:baseline-search", width=20),"Ver Mais"], color="white"), href=f'{cards_list.link}', target="_blank", className="btn btn-primary")]
                            , position="apart")
                    ]
                ), class_name="mt-3 apex-result-card"
)
    
    return card_append

def google_search(query: str, num_result=None, as_sitesearch='google'):
    settings = get_settings()
    result_limit = num_result or settings.search_results_per_source
    search_results = []
    if current_user.serpapi_key:
        if as_sitesearch == 'google':
            payload = {
            "q": query,
            "gl": "br",
            "hl": "pt-br",
            "num": result_limit,
            }
            data = _serper_post("news", payload)

            if 'news' in data:
                for result in _limited_results(data['news'], result_limit):
                    search_results.append(normalize_search_result(result))
            return search_results
        elif as_sitesearch == 'twitter':
            payload = {
            "q": query + " (site:twitter.com OR site:x.com)",
            "gl": "br",
            "hl": "pt-br",
            "num": result_limit,
            }
            data = _serper_post("search", payload)
            if 'organic' in data:
                for result in _limited_results(data['organic'], result_limit):
                    search_results.append(normalize_search_result(result))
            return search_results
        elif as_sitesearch == 'facebook':
            payload = {
            "q": query + " site:facebook.com",
            "gl": "br",
            "hl": "pt-br",
            "num": result_limit,
            }
            data = _serper_post("search", payload)
            if 'organic' in data:
                for result in _limited_results(data['organic'], result_limit):
                    search_results.append(normalize_search_result(result))
            return search_results
    return search_results
