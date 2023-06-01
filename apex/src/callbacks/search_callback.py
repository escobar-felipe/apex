from dash_extensions.enrich import Output, Input, State, callback, no_update
from src.utils.functions import google_search, Card, create_cards
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from flask_login import current_user

output = [
    Output('google_tittle', 'rightSection'),
    Output('twitter_tittle', 'rightSection'),
    Output('facebook_tittle', 'rightSection'),
    Output('chatgpt_tittle', 'disabled'),
    Output('google_tabs', 'children'),
    Output('twitter_tabs', 'children'),
    Output('facebook_tabs', 'children'),
    Output('search_value', 'data'),
    Output('search_links', 'data'),
    Output('search-text', 'children'),
    Output('qtd-text', 'children'),
    Output('alert-div', 'children'),
    Output('button-report', 'disabled'),
    Output('multiselect-text','data')
]

@callback(output,
          [Input('button-search', 'n_clicks')],
          [State('search-state', 'value')], prevent_initial_call=True)
def search_callback(n_clicks, search_query):
    disabled = False
    if search_query:
        search_google = google_search(search_query)
        search_twitter = google_search(query=str(search_query), as_sitesearch="twitter.com")
        search_facebook = google_search(query=str(search_query), as_sitesearch="facebook.com")

        badge_google = dmc.Badge(
                            len(search_google),
                            size="xs",
                            p=0,
                            variant="filled",
                            sx={"width": 16, "height": 16, "pointerEvents": "none"},
                        )
        badge_twitter = dmc.Badge(
                        len(search_twitter),
                        size="xs",
                        p=0,
                        variant="filled",
                        sx={"width": 16, "height": 16, "pointerEvents": "none"},
                    )
        badge_facebook = dmc.Badge(
                        len(search_facebook),
                        size="xs",
                        p=0,
                        variant="filled",
                        sx={"width": 16, "height": 16, "pointerEvents": "none"},
                    )
        articles = []
        data = []
        cards_google = []
        cards_twitter = []
        cards_facebook = []
        for i in search_google:
            cards_google.append(create_cards(Card(i['title'],i['description'],i['source'], i['link'])))
            dict_valeus = {
                'brand': search_query,
                'title': i['title'],
                'link': i['link'],
                'description':i['description'],
                'source': i['source']
            }
            data.append({"value":dict_valeus, "label":i['title'][:40] })
            articles.append(dict_valeus)
        for i in search_twitter:
            cards_twitter.append(create_cards(Card(i['title'],i['description'], i['source'], i['link'])))
        for i in search_facebook:
            cards_facebook.append(create_cards(Card(i['title'],i['description'], i['source'], i['link'])))

        if len(cards_facebook)==0:
            cards_facebook.append(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Não foram encontrados resultados"], className="m-2 mt-5")]))
        if len(cards_twitter)==0:
            cards_twitter.append(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Não foram encontrados resultados"], className="m-2 mt-5")]))
        if len(cards_google)==0:
            cards_google.append(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Não foram encontrados resultados"], className="m-2 mt-5")]))

        qtd_textos  = str(len(articles)) + " Textos"
        items = []
        
        if not current_user.api_key:
            items.append(dmc.ListItem("Necessário cadastrar uma chave Openai API")) 

        if len(items)>0:
            disabled = True
            list_items = dmc.Alert(
                        dmc.List(items),
                        title="Impossível gerar relatório!",
                        className='mt-3',
                        color="red"
                    )
        else:
            list_items = no_update
        
        
        return badge_google,badge_twitter,badge_facebook,False,cards_google,cards_twitter,cards_facebook,search_query,articles,search_query, qtd_textos,list_items, disabled, data
    else:
        return no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update, no_update
