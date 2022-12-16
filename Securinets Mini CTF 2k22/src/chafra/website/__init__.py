from flask import Flask
import os


def createApp():
    app = Flask(__name__, static_url_path="/assets")

    from .routes.views import web
    app.register_blueprint(web, url_prefix='/')
    
    return app


