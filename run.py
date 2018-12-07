"""
ccextractor-web | run.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import os

from flask import Flask, g, session, render_template
from template import LayoutHelper
from database import db
from logger import Logger
from config_parser import general_config

from mod_landing.controller import mod_landing
from mod_auth.controller import mod_auth
from mod_dashboard.controller import mod_dashboard
from mod_kvm.controller import mod_kvm
from mod_dashboard.models import DetailsForTemplate

app = Flask(__name__, instance_relative_config=True)

app.config.from_mapping(general_config)
app.config.from_pyfile('config.py')  # secret configurations : 'instance/config.py'

# creating logger object
logger = Logger(log_level=app.config['LOG_LEVEL'],
                dir=app.config['LOG_FILE_DIR'],
                filename="log")
log = logger.get_logger("app")

log.debug("Configuration loaded.")
log.debug("Logger created.")

db.init_app(app)
log.debug("flask-sqlaclchemy (db) object created.")


# Registering blueprint for all modules
app.register_blueprint(mod_landing)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_dashboard)

if app.config['ENABLE_KVM']:
    app.register_blueprint(mod_kvm)

log.debug("Blueprints registered.")


def init_app() -> bool:
    """
        Summary
        ----------
        Initialises the application on deployment.

        Details
        ----------
        This function runs before the very first request is processed by the application after deployment.

        - Initialises database with pre-existing values needed for app functioning.
            > If the values don't exist, create them.

        - Set up 'Application Mode' (either Public or Local) depending on configuration.
            Config variable : 'ENABLE_LOCAL_MODE'
            Possible values : True, False

            > If 'Local Mode' (ENABLE_LOCAL_MODE == True)
                - To use when deploying the app on local/private server for personal/single/isolated use.
                - Creates an Admin User, with credentials from secret config (instance/config.py)
                - By default logs in as this admin user.
                - All the operations (upload, processing, deletion etc. are done through this account.
                - There still exist the capability to create (and login as) other users.

            > If 'Public Mode' (ENABLE_LOCAL_MODE == False)
                - To use when deploying the app on public server, where different people can access the app.
                - No default account is created.
                - Each user creates their own account and all operations are under their account.
                - Admin account can be created by granting 'Role' as 'admin'.

        Returns
        -------
        bool
            True if successful, False otherwise.
    """

    log.debug('INIT : Creating admin account.')
    from mod_auth.models import Users, AccountType
    email = app.config['ADMIN_EMAIL']
    admin_user = Users.query.filter(Users.email == app.config['ADMIN_EMAIL']).first()

    if admin_user is None:
        admin_user = Users(email=email,
                           name=app.config['ADMIN_NAME'],
                           password=app.config['ADMIN_PWD'],
                           account_type=AccountType.admin)
        db.session.add(admin_user)
        db.session.commit()

        log.debug('Created admin account for : {email}, ID : {id}'.format(email=email, id=admin_user.id))
    else:
        log.debug('Failed to create admin account for : {email}, account already exists.'.format(email=email))

    # Setting 'Application Mode'
    log.debug('INIT : Checking app mode.')
    if app.config['ENABLE_LOCAL_MODE']:
        log.debug('LOCAL MODE ENABLED')

        try:
            if g.user is not None:
                log.debug('Account found in session, id = {id} '.format(id=g.user.id))

                if g.user.id == admin_user.id:
                    log.debug('Logged in as admin account for : {email}.'.format(email=email))
                else:
                    log.debug('Failed to login using admin account for : {email}, {id} already logged in.'.format(email=email, id=g.user.id))

        except Exception:
            log.debug('No account found in session, adding admin account to session.')
            session['user_id'] = admin_user.id

        else:
            log.debug('User ID with no account found in session. Appending admin account to global logged in user.')

            user_id = session.get('user_id', 0)
            g.user = Users.query.filter(Users.id == user_id).first()

    else:
        log.debug('PUBLIC MODE ENABLED')

    return True


@app.template_filter()
def timesince(dt, default="just now", precision=0):
    """
        Summary
        ----------
        Returns string representing "time since" e.g. 3 days ago, 5 hours ago etc.

        Details
        ----------
        This snippet adds a 'timesince' filter for jinja2 template (used by Flask) while rendering the web pages. The
        filter takes a datetime object (dt) and subtracts it with the current time to get the difference in times.
        If the difference period is greater than 1 (integer) value, it chooses the respective period value.

        Examples
        --------

        In the template, if the variable `file.upload_timestamp` store a datetime object, then
            <h1> Uploaded {{ file.upload_timestamp|timesince }} </h1>

        Output : <h1> Uploaded 2 hours ago </h1>

        Parameters
        ----------
        dt : datetime
            The datetime object upto which the passed time is to be calculated.
        default : str
            The default value to be returned when the difference does not fall in any of the periods. e.g 'just now'.
        precision : int
            Decimal places to show in the surpassed time. E.g. if precision = 1, output = 1.2 weeks ago.

        Returns
        -------
        str
            String representation of the time since given datetime object.
    """
    from datetime import datetime
    if dt.tzinfo is None:
        now = datetime.now()
    else:
        from datetime import timezone
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
            return '{period:.{precision}f} {period_name} ago'.format(period=period,
                                                                     precision=precision,
                                                                     period_name=singular if period == 1 else plural)

    return default


@app.before_first_request
def before_first_request():
    """
        Summary
        ----------
        Runs the contained functions before the very first request is processed by the application after deployment.

        Details
        ----------
        Contains the functions which are needed to be executed before the very first request to the application is
        received. Involves

        - Creating tables in the databases from models (if they don't already exist)
        - Initialising application with required configuration and database values
        - Creating directories upon which the app depends
    """

    log.debug('INIT : Preparing database.')
    db.create_all()

    log.debug('INIT : Initialising app.')
    init_app()

    if app.config['ENABLE_KVM']:
        log.debug('INIT : Initialising KVM.')
        from mod_kvm.controller import init_kvm_db
        init_kvm_db()

    # creating directories if they don't exist
    os.makedirs(os.path.dirname(os.path.join(app.config['TEMP_UPLOAD_FOLDER'])), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.join(app.config['VIDEO_REPOSITORY'])), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.join(app.config['LOGS_DIR'])), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.join(app.config['OUTPUT_DIR'])), exist_ok=True)


@app.errorhandler(404)
def page_not_found_handler(e):
    """
    Handles the 404 error and displays a template.
    """
    if g.user is not None:
        details = DetailsForTemplate(g.user.id, admin_dashboard=False)
        layout = LayoutHelper(logged_in=True, details=details)
    else:
        layout = LayoutHelper(logged_in=False)
    return render_template('404.html', layout=layout.get_entries()), 404


@app.errorhandler(500)
def internal_server_error_handler(e):
    """
    Handles the 500 error and displays a template.
    """
    if g.user is not None:
        details = DetailsForTemplate(g.user.id, admin_dashboard=False)
        layout = LayoutHelper(logged_in=True, details=details)
    else:
        layout = LayoutHelper(logged_in=False)
    return render_template('500.html', layout=layout.get_entries()), 500


if __name__ == '__main__':
    log.debug("Running App.")
    app.run(host='0.0.0.0')
