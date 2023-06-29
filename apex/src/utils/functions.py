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

def google_search(query:str, num_result=15,as_sitesearch=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    search_results = []
    query = query.replace(" ","+")
    if as_sitesearch == 'facebook.com':
        query += "+publicação"
    if as_sitesearch:
        url =  f"https://www.google.com/search?q={query}&hl=pt-BR&num={num_result}&as_sitesearch={as_sitesearch}&as_qdr=d2"
    else:
        url = f"https://www.google.com/search?q={query}&hl=pt-BR&num={num_result}&as_qdr=d2"

    search_results = []
    if current_user.serpapi_key:
        params = {
            "api_key": current_user.serpapi_key,
            "engine": "google",
            "q": query,
            "hl": "pt",
            "tbm": "nws",
            "num": num_result,
            "as_qdr":"d2"
        }
        #define os parâmetros de pesquisa na SERPAPI 
        response = requests.get('https://serpapi.com/search.json', params=params)
        #utilizando a lib requests para solicitar a requisição e receber a resposta(response)
        data = json.loads(response.text)
        #cria um json com a resposta

        if 'news_results' in data:
            #verifica se o json contém a chave 'new_results'
            #cria uma lista vazia
            for result in data['news_results']:
                #para cada resultado(lista) nos valores da chave 'new_results' 
                search_results.append({
                    'title': result['title'],
                    'link': result['link'],
                    'description':f"{result['date']} - {result['snippet']}",
                    'source': result['source']
                })
    #             #adiciona um dicionário na lista articles com os seguintes valores: title, link, date e source
    #     else:
    #         return []
    return search_results

    # return [dict(t) for t in {tuple(d.items()) for d in search_results}]

# def get_google_news_data(query, num_results=10): #"pegar" os resultados novos do google de acordo com "query" que foi passada
#         print('serpapi')
#         params = {
#             "api_key": current_user.serpapi_key,
#             "engine": "google",
#             "q": query,
#             "hl": "pt",
#             "tbm": "nws",
#             "num": num_results,
#             "as_qdr":"d2"
#         }
#         #define os parâmetros de pesquisa na SERPAPI 
#         response = requests.get('https://serpapi.com/search.json', params=params)
#         #utilizando a lib requests para solicitar a requisição e receber a resposta(response)
#         data = json.loads(response.text)
#         #cria um json com a resposta

#         if 'news_results' in data:
#             #verifica se o json contém a chave 'new_results'
#             #se sim:
#             articles = []
#             #cria uma lista vazia
#             for result in data['news_results']:
#                 #para cada resultado(lista) nos valores da chave 'new_results' 
#                 articles.append({
#                     'title': result['title'],
#                     'link': result['link'],
#                     'date': result['date'],
#                     'description':result['snippet'],
#                     'source': result['source']
#                 })
#                 #adiciona um dicionário na lista articles com os seguintes valores: title, link, date e source
#             return articles
#             #retorna a lista articles
#         else:
#             #se não, retorna lista vazia e printa "nenhum resultado encontrado"
#             print("No news results found.")
#             return []