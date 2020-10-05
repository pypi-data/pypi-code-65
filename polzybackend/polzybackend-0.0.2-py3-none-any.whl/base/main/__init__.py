from flask import Blueprint

bp = Blueprint('main', __name__)

from base.main import routes