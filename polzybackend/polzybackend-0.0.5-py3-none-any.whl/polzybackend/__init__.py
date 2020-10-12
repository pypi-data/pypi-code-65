from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPTokenAuth
import os


# initialization
db = SQLAlchemy()
migrate = Migrate()
auth = HTTPTokenAuth(scheme='Bearer')

def create_app(config=None):
    # create application
    app = Flask(__name__)
    # set default config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', default = 'secret!key')
    app.config['JSON_SORT_KEYS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        default='sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'polzy.db'),
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .main import bp
    app.register_blueprint(bp)

    return app



from . import models
