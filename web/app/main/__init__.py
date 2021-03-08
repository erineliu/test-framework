from flask import Blueprint

app2_bp = Blueprint('app2', __name__)


from . import main_pages,main_api
