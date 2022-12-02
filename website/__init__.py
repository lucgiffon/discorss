from flask import Flask

from .auth import auth_blueprint
from .views import views_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevConfig')  # config file path relative to where the app is run (root directory)

    register_blueprints(app)

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(views_blueprint, url_prefix="/")
    app.register_blueprint(auth_blueprint, url_prefix="/")
