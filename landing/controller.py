from flask import Blueprint

landing = Blueprint("landing", __name__)


@landing.route('/')
def index():
    return "May the twenty fourth be with you! :)"
