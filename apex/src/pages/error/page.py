from dash import html, register_page,dcc

register_page(__name__, path='/error', title="Error")

def layout(**query_string):
    return dcc.Location(pathname="/login", id="redirec-22")