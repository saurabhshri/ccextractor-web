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

from config_parser import general_config

#creating Flask app object
app = Flask(__name__, instance_relative_config=True)

app.config.from_mapping(general_config)
app.config.from_pyfile('config.py') # secret configurations : 'instance/config.py'

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

@app.template_filter()
def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    diff = now - dt

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        if period >= 1:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default

@app.before_first_request
def before_first_request():
    db.create_all()
    init_db()

    #create directories if they don't exist
    os.makedirs(os.path.dirname(os.path.join(app.config['TEMP_UPLOAD_FOLDER'])), exist_ok=True)

if __name__ == '__main__':
    log.debug("Running App.")
    app.run(host='0.0.0.0')
