
from importlib import import_module
import pathlib
from flask import Flask
from src.config import get_settings

def load_extensions(app: Flask):
    settings = get_settings()
    
    folder = 'src/ext'
    
    for ext in settings.extensions:
        file = pathlib.Path(f'{folder}/{ext}.py')

        data = str(file)
        
        module_name = data.replace('/', '.').replace('.py', '')         
    
        ext = import_module(module_name)
        
        if 'init_app' in dir(ext):
            ext.init_app(app)
            