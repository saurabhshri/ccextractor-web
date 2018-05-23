from flask import Blueprint, render_template
from mod_auth.models import User
from database import db

mod_auth = Blueprint("mod_auth", __name__)

@mod_auth.route('/db')
def indexDB():

    admin = User(username="admin", email="lol@llo.com")
    db.session.add(admin)
    db.session.commit()

    return "May the twenty fourth be with you! :)"
