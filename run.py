"""
ccextractor-web | run.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54@gmail.com
Link     : https://github.com/saurabhshr

"""

import sys

# 3rd party imports
from flask import Flask

# modules and internal imports
from config import app_config
from database import db

from landing.controller import landing
from mod_auth.controller import mod_auth
from mod_dashboard.controller import mod_dashboard

#creating Flask app object
app = Flask(__name__, instance_relative_config=True)

#creating flask-sqlaclchemy (db) object
db.init_app(app)

# Registering blueprint for all modules
app.register_blueprint(landing)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_dashboard)

#creating configuration : pass 'development' / 'production' / 'local' as parameter while running app
def createConfig():

    configuration_environment = "development"

    if len(sys.argv) > 1:
        configuration_environment = sys.argv[1]

    if configuration_environment not in app_config:
        #print("Invalid Configuration, Possible Values : development/production. Setting to development.")
        configuration_environment = "development"

    app.config.from_object(app_config[configuration_environment])
    app.config.from_pyfile('config.py') # secret configurations

@app.before_first_request
def before_first_request():
    db.create_all()

if __name__ == '__main__':
    createConfig()
    app.run()
