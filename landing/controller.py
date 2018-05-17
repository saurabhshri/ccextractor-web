from flask import Blueprint, render_template

landing = Blueprint("landing", __name__)

@landing.route('/')
def index():
    return "May the twenty fourth be with you! :)"
