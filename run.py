"""
ccextractor-web | run.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import os

# 3rd party imports
from flask import Flask, g

# modules and internal imports
from config import app_config
from database import db
from logger import Logger

from landing.controller import landing
from mod_auth.controller import mod_auth
from mod_dashboard.controller import mod_dashboard
from mod_kvm.controller import mod_kvm


#creating Flask app object
app = Flask(__name__, instance_relative_config=True)

#creating configuration : set FLASK_ENV as 'development' / 'production' / 'local'
configuration_environment = os.environ.get('FLASK_ENV', 'development')

if configuration_environment not in app_config:
    #print("Invalid Configuration, Possible Values : development/production/local. Setting to development.")
    configuration_environment = "development"

app.config.from_object(app_config[configuration_environment])
app.config.from_pyfile('config.py') # secret configurations

# creating logger object
logger = Logger(log_level=app.config['LOG_LEVEL'],
                dir=app.config['LOG_FILE_DIR'],
                filename="log")
log = logger.get_logger("app")

log.debug("Configuration loaded.")
log.debug("Logger created.")

#creating flask-sqlaclchemy (db) object
db.init_app(app)
log.debug("flask-sqlaclchemy (db) object created.")


# Registering blueprint for all modules
app.register_blueprint(landing)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_dashboard)
app.register_blueprint(mod_kvm)
log.debug("Blueprints registered.")

def init_db():
    from mod_dashboard.models import CCExtractorVersions
    ccextractor = CCExtractorVersions.query.all()
    print(ccextractor)
    if not ccextractor:
        ccextractor = CCExtractorVersions('1', '22222', 'build/ccextractor', 'build/ccextractor', 'build/ccextractor')
        db.session.add(ccextractor)
        db.session.commit()

@app.before_first_request
def before_first_request():
    db.create_all()
    init_db()

    #create directories if they don't exist
    os.makedirs(os.path.dirname(os.path.join(app.config['TEMP_UPLOAD_FOLDER'])), exist_ok=True)

if __name__ == '__main__':
    log.debug("Running App.")
    app.run(host='0.0.0.0')
