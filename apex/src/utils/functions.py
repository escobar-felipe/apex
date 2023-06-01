import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash import html
from typing import List
from dash_iconify import DashIconify
import requests
from bs4 import BeautifulSoup


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
    result_count = 0
    page_count = 0
    query = query.replace(" ","+")
    if as_sitesearch == 'facebook.com':
        query += "+publicação"
    if as_sitesearch:
        url =  f"https://www.google.com/search?q={query}&hl=pt-BR&num={num_result}&as_sitesearch={as_sitesearch}&as_qdr=d2"
    else:
        url = f"https://www.google.com/search?q={query}&hl=pt-BR&num={num_result}&as_qdr=d2"
    while  page_count <1:
        response = requests.get(url, headers=headers)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            for i, result in enumerate(soup.find_all('div', class_='g')):
                try:
                    title = result.find('h3').get_text()
                    link = result.find('a')['href'][:]
                    font = result.find_all('span', {'class':'VuuXrf'})[0].text
                except:
                    title = ''
                    link = ''
                    font = ''
                try:
                    span = result.find_all(name='div', class_='MUxGbd')[0].text
                except:
                    span = ''
                
                if not span=='' or not link=='':
                    search_results.append({'title': title, 'link': link, 'description':span, 'source':font})
                result_count += 1

            page_count += 1
        else:
            return []

    return [dict(t) for t in {tuple(d.items()) for d in search_results}]