
from flask import Flask
from memori_exe_builder.api import api



    
def create_app(settings_overrides=None):
   
    app = Flask(__name__)
    configure_settings(app, settings_overrides)
    configure_blueprints(app)
    return app


def configure_settings(app, settings_override):
    app.config.update({
        'DEBUG': False,
        'TESTING': False,
    })
    if settings_override:
        app.config.update(settings_override)


def configure_blueprints(app):
    app.register_blueprint(api)