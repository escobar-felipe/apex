
from dash_bootstrap_components.themes import BOOTSTRAP
from flask import Flask
from dash_extensions.enrich import MultiplexerTransform, DashProxy
import os
import src.callbacks

assets_path = os.getcwd() +'/assets'

dash_app = DashProxy(__name__,
    use_pages=True,
    title='Cfit',
    suppress_callback_exceptions=True,
    transforms=[MultiplexerTransform()], 
    serve_locally=True,
    assets_folder=assets_path,
    update_title='carregando...',
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    url_base_pathname='/',
    external_stylesheets=[BOOTSTRAP],
    external_scripts = [{'src': 'https://unpkg.com/imask@6.4.3/dist/imask.js'},
                        {'src': 'https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/dayjs.min.js'},
                        {'src': 'https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/locale/pt-br.min.js'}]
)


def init_app(app: Flask):
    
    dash_app.init_app(app)
        
    app.app_context().push()
    
    
