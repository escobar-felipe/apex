from dash_extensions.enrich import Output, Input, State, callback, no_update, ctx
from src.utils.functions import google_search, Card, create_cards, SearchProviderError, validate_serper_api
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from flask_login import current_user
from src.ext.database import db
from src.models import SearchAudit
from src.utils.tenancy import get_current_tenant_id

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


def record_search_audit(query, status, result_counts=None, error_message=None):
    audit = SearchAudit(
        tenant_id=get_current_tenant_id(),
        user_id=current_user.id if current_user.is_authenticated else None,
        search_query=query or "",
        status=status,
        provider="serper",
        result_counts=result_counts,
        error_message=(error_message or "")[:512] or None,
    )
    db.session.add(audit)
    db.session.commit()

@callback(output,
          [Input('button-search', 'n_clicks')],
          [State('search-state', 'value')], prevent_initial_call=True)
def search_callback(n_clicks, search_query):
    print(ctx)
    disabled = False
    if search_query:
        try:
            validate_serper_api()
            search_google = google_search(search_query)
            search_twitter = google_search(query=str(search_query), as_sitesearch="twitter")
            search_facebook = google_search(query=str(search_query), as_sitesearch="facebook")
        except SearchProviderError as error:
            record_search_audit(search_query, "error", error_message=str(error))
            alert = dmc.Alert(
                str(error),
                title="Erro na pesquisa",
                className='mt-3',
                color="red"
            )
            empty_state = dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Não foi possível buscar resultados"], className="m-2 mt-5")], className="apex-empty-state")
            return (
                dmc.Badge(0, size="xs", p=0, color="#504cab", variant="filled", sx={"width": 16, "height": 16, "pointerEvents": "none"}),
                dmc.Badge(0, size="xs", p=0, color="#504cab", variant="filled", sx={"width": 16, "height": 16, "pointerEvents": "none"}),
                dmc.Badge(0, size="xs", p=0, color="#504cab", variant="filled", sx={"width": 16, "height": 16, "pointerEvents": "none"}),
                True,
                [empty_state],
                [empty_state],
                [empty_state],
                search_query,
                [],
                search_query,
                "0 Textos",
                alert,
                True,
                []
            )
        record_search_audit(
            search_query,
            "success",
            result_counts={
                "google_news": len(search_google),
                "x_twitter": len(search_twitter),
                "facebook": len(search_facebook),
            },
        )

        badge_google = dmc.Badge(
                            len(search_google),
                            size="xs",
                            p=0,
                            color="#504cab",
                            variant="filled",
                            sx={"width": 16, "height": 16, "pointerEvents": "none"},
                        )
        badge_twitter = dmc.Badge(
                        len(search_twitter),
                        size="xs",
                        p=0,
                        color="#504cab",
                        variant="filled",
                        sx={"width": 16, "height": 16, "pointerEvents": "none"},
                    )
        badge_facebook = dmc.Badge(
                        len(search_facebook),
                        size="xs",
                        p=0,
                        color="#504cab",
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
            data.append({"value":dict_valeus, "label":i['title'][:50] })
            articles.append(dict_valeus)
        for i in search_twitter:
            cards_twitter.append(create_cards(Card(i['title'],i['description'], i['source'], i['link'])))
        for i in search_facebook:
            cards_facebook.append(create_cards(Card(i['title'],i['description'],  i['source'], i['link'])))

        if len(cards_facebook)==0:
            cards_facebook.append(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Não foram encontrados resultados"], className="m-2 mt-5")]))
        if len(cards_twitter)==0:
            cards_twitter.append(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Não foram encontrados resultados"], className="m-2 mt-5")]))
        if len(cards_google)==0:
            cards_google.append(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Não foram encontrados resultados"], className="m-2 mt-5")]))

        qtd_textos  = str(len(articles)) + " Textos"
        items = []
        
        if not current_user.api_key:
            items.append(dmc.ListItem("Cadastre uma chave OpenAI API em Minha Conta.")) 

        if len(items)>0:
            disabled = True
            list_items = dmc.Alert(
                        dmc.List(items),
                        title="Não é possível gerar o relatório",
                        className='mt-3',
                        color="red"
                    )
        else:
            list_items = no_update
        
        
        return badge_google,badge_twitter,badge_facebook,False,cards_google,cards_twitter,cards_facebook,search_query,articles,search_query, qtd_textos,list_items, disabled, data
    else:
        return no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update, no_update
