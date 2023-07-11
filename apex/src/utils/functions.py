import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash import html
from typing import List
from dash_iconify import DashIconify
import requests
from bs4 import BeautifulSoup
from flask_login import current_user
import json



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
                        html.P(cards_list.body),
                        dmc.Group([
                            html.P(dmc.Text(["fonte: " +cards_list.source], weight=700, color="gray",className="mb-2")),
                            html.A(dmc.Text([DashIconify(icon="ic:baseline-search", width=20),"Ver Mais"], color="white"), href=f'{cards_list.link}', target="_blank", className="btn btn-primary")]
                            , position="apart")
                    ]
                ), class_name="mt-3"
)
    
    return card_append

def google_search(query:str, num_result=15,as_sitesearch='google'):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    search_results = []
    query = query.replace(" ","+")
    search_results = []
    if current_user.serpapi_key:
        if as_sitesearch == 'google':
            url = "https://google.serper.dev/news"
            payload = json.dumps({
            "q": query,
            "gl": "br",
            "hl": "pt-br"
            })
            headers = {
            'X-API-KEY': current_user.serpapi_key,
            'Content-Type': 'application/json'
            }
            #define os parâmetros de pesquisa na SERPAPI 
            # response = requests.get('https://serpapi.com/search.json', params=params)
            response = requests.request("POST", url, headers=headers, data=payload)
            #utilizando a lib requests para solicitar a requisição e receber a resposta(response)
            data = json.loads(response.text)
            #cria um json com a resposta

            if 'news' in data:
                #verifica se o json contém a chave 'new_results'
                #cria uma lista vazia
                for result in data['news']:
                    #para cada resultado(lista) nos valores da chave 'new_results' 
                    search_results.append({
                        'title': result['title'],
                        'link': result['link'],
                        'description':f"{result.get('date', 'Data não informada')} - {result['snippet']}",
                        'source': result['source']
                    })
        #             #adiciona um dicionário na lista articles com os seguintes valores: title, link, date e source
        #     else:
        #         return []
            return search_results
        elif as_sitesearch == 'twitter':
            url = "https://google.serper.dev/search"
            payload = json.dumps({
            "q": query + "twitter",
            "gl": "br",
            "hl": "pt-br"
            })
            headers = {
            'X-API-KEY': current_user.serpapi_key,
            'Content-Type': 'application/json'
            }
            #define os parâmetros de pesquisa na SERPAPI 
            # response = requests.get('https://serpapi.com/search.json', params=params)
            response = requests.request("POST", url, headers=headers, data=payload)
            #utilizando a lib requests para solicitar a requisição e receber a resposta(response)
            data = json.loads(response.text)
            if 'organic' in data:
                #verifica se o json contém a chave 'new_results'
                #cria uma lista vazia
                for result in data['organic']:
                    #para cada resultado(lista) nos valores da chave 'new_results' 
                    search_results.append({
                        'title': result['title'],
                        'link': result['link'],
                        'description':f"{result.get('date', 'Data não informada')} - {result['snippet']}",
                        'source': result.get('source',"Fonte não identificada")
                    })
        #             #adiciona um dicionário na lista articles com os seguintes valores: title, link, date e source
        #     else:
        #         return []
            return search_results

