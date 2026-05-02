from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',   # Fixed path
                static_folder='../static')        # Fixed path
    
    app.config.from_object(Config)

    from app.routes import main
    app.register_blueprint(main)

    return app