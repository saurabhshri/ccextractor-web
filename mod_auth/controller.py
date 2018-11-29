"""
ccextractor-web | mod_auth/controller.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
from mail import send_simple_message

import hmac
import hashlib
import time

from functools import wraps

from database import db
from logger import Logger
from template import LayoutHelper

from mod_auth.models import Users
from mod_auth.forms import SignupEmailForm, SignupForm, LoginForm

from config_parser import general_config


user_logger = Logger(log_level=general_config['LOG_LEVEL'],
                     dir=general_config['LOG_FILE_DIR'],
                     filename="users")
user_log = user_logger.get_logger("users")

mod_auth = Blueprint("mod_auth", __name__)


@mod_auth.before_app_request
def before_app_request():
    user_id = session.get('user_id', 0)
    g.user = Users.query.filter(Users.id == user_id).first()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            user_log.warning('[IP: {ip}] tried to access {endpoint} without logging in.'.format(ip=request.remote_addr, endpoint=request.endpoint))
            flash('You need to login first.', 'error')
            return redirect(url_for('mod_auth.login', next=request.endpoint))

        return f(*args, **kwargs)

    return decorated_function


def check_account_type(account_types=None, parent_route=None):
    def access_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user.account_type in account_types:
                return f(*args, **kwargs)
            user_log.warning('[User: {user_id}] account type : {user_acc_type} tried to access {endpoint} without {req_acc_types} privilege(s).'.format(user_id=g.user.id, user_acc_type=g.user.account_type, endpoint=request.endpoint, req_acc_types=account_types))
            flash('Your account does not have enough privileges to access this functionality.', 'error')
            return redirect(url_for('mod_dashboard.dashboard'))
        return decorated_function
    return access_decorator


@mod_auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if g.user is not None:
        flash('Currently logged in as ' + g.user.username, 'success')
        return redirect(url_for('mod_dashboard.dashboard'))

    form = SignupEmailForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is not None:
            flash('Email is already registered!', 'error')
            user_log.error('Duplicate registration attempt for : {email}, registered with user : {user}'.format(email=form.email.data, user=user.id))
            return redirect(url_for('.login'))
        else:
            expires = int(time.time()) + 86400
            verification_code = generate_verification_code(
                "{email}{expires}".format(email=form.email.data, expires=expires))
            resp = send_verification_mail(form.email.data, verification_code, expires)

            if resp.status_code is not 200:
                flash('Unable to send verification email. Please get in touch.', 'error')
                from run import log
                log.error("Mail sending failed. Check mail logs.")

            else:
                user_log.debug('Received registration request for : {email}'.format(email=form.email.data))
                flash('Please check your email for verification and further instructions.', 'success')

    layout = LayoutHelper(logged_in=False)
    return render_template("mod_auth/signup.html", form=form, layout=layout.get_entries())


def generate_verification_code(data):
    from flask import current_app as app
    key = app.config.get('HMAC_KEY')

    key_bytes = bytes(key, 'latin-1')
    data_bytes = bytes(data, 'latin-1')

    return hmac.new(key_bytes, data_bytes, hashlib.sha256).hexdigest()


def send_verification_mail(email, verification_code, expires):

    from flask import current_app as app

    verification_url = app.config['ROOT_URL'] + '/verify'
    subject = "Please verify your email address for account activation."
    body = render_template('mod_auth/verification_mail.html', url=verification_url, email=email,
                           verification_code=verification_code, expires=expires)
    return send_simple_message(email, subject, str(body))


@mod_auth.route('/verify/<string:email>/<string:received_verification_code>/<int:expires>', methods=['GET', 'POST'])
def verify_account(email, received_verification_code, expires):

    if g.user is not None:
        flash('Currently logged in as ' + g.user.username, 'success')
        return redirect(url_for('mod_dashboard.dashboard'))

    if time.time() <= expires:

        expected_verification_code = generate_verification_code("{email}{expires}".format(email=email, expires=expires))

        if hmac.compare_digest(expected_verification_code, received_verification_code):
            flash('Verification complete! Proceed to signup.', 'success')
            user = Users.query.filter_by(email=email).first()
            if user is None:
                form = SignupForm()
                if form.validate_on_submit():
                    user = Users(email=email,
                                 password=form.password.data,
                                 name=form.name.data)
                    db.session.add(user)
                    db.session.commit()

                    resp = send_signup_confirmation_mail(user.email)
                    if resp.status_code is not 200:
                        from run import log
                        log.debug("Mail sending failed. Check mail logs.")

                    user_log.debug("Sign Up Complete for : {email} | User ID: {user_id}".format(email=user.email, user_id=user.id))
                    flash('Signup Complete! Please Login to continue.', 'success')
                else:
                    layout = LayoutHelper(logged_in=False)
                    return render_template("mod_auth/signup-verification.html", form=form, email=email, layout=layout.get_entries())
            else:
                flash('Email is already registered!', 'error')
            return redirect(url_for('.login'))

        flash('Verification failed! Incorrect email address/verification code. Please try again.', 'error-message')
    else:
        flash('The verification link is expired. Please try again.', 'error-message')

    return redirect(url_for('.signup'))


def send_signup_confirmation_mail(email):
    subject = "Account creation successful!"
    body = render_template('mod_auth/signup_confirmation.html')
    return send_simple_message(email, subject, str(body))


@mod_auth.route('/login', methods=['GET', 'POST'])
def login():
    user_id = session.get('user_id', 0)
    g.user = Users.query.filter(Users.id == user_id).first()

    redirect_location = request.args.get('next', '')

    if g.user is not None:
        flash('Logged in as ' + g.user.username, 'success')
        if len(redirect_location) == 0:
            return redirect(url_for('mod_dashboard.dashboard'))
        else:
            return redirect(url_for(redirect_location))

    form = LoginForm(request.form)

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and user.is_password_valid(form.password.data):
            session['user_id'] = user.id
            user_log.debug('[User: {user_id}] logged in from IP: {ip}'.format(user_id=user.id, ip=request.remote_addr))
            if len(redirect_location) == 0:
                return redirect(url_for('mod_dashboard.dashboard'))
            else:
                return redirect(url_for(redirect_location))
        else:
            flash('Wrong username or password', 'error')
            user_log.warning('Invalid login attempt from IP: {ip} for email :{email}'.format(email=form.email.data, ip=request.remote_addr))

        return redirect(url_for('.login'))
    layout = LayoutHelper(logged_in=False)
    return render_template("mod_auth/login.html", form=form, layout=layout.get_entries(), next=redirect_location)


@mod_auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    files = g.user.files
    return render_template("mod_auth/profile.html", user=g.user, files=files)


@mod_auth.route('/logout')
def logout():
    user_log.debug('[User: {user_id}] logged out from IP: {ip}'.format(user_id=g.user.id, ip=request.remote_addr))
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('.login'))
