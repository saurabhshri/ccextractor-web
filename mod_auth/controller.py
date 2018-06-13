"""
ccextractor-web | mod_auth/controller.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g, abort
from email_validator import validate_email, EmailNotValidError
from mail import send_simple_message

from database import db
from functools import wraps

from mod_auth.models import Users
from mod_auth.forms import SignupForm, LoginForm
mod_auth = Blueprint("mod_auth", __name__)

@mod_auth.before_app_request
def before_app_request():
    user_id = session.get('user_id', 0)
    g.user = Users.query.filter(Users.id == user_id).first()

def generate_username(email):
    #TODO : Disallow a set of usernames such as 'admin'
    base_username = username = email.split('@')[0]
    count_suffix = 1
    while True:
        user = Users.query.filter_by(username=username).first()
        if user is not None:
            username = '{base_username}-{count_suffix}'.format(base_username=base_username, count_suffix=str(count_suffix))
            count_suffix += 1
        else:
            break

    return username

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('You need to login first.', 'error')
            return redirect(url_for('mod_auth.login', next=request.endpoint))

        return f(*args, **kwargs)

    return decorated_function


@mod_auth.route('/signup', methods=['GET', 'POST'])
def signup():

    if g.user is not None:
        flash('Currently logged in as ' + g.user.username, 'success')
        return redirect(url_for('.profile'))

    form = SignupForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(username=generate_username(form.email.data),
                         email=form.email.data,
                         password=form.password.data,
                         name=form.name.data)
            db.session.add(user)
            db.session.commit()

            send_verification_mail(user.email, user.verification_code)

            flash('Signup Complete! Please verify your email address to activate your account!', 'success')

        else:
            flash('Email is already registered!', 'error')

        return redirect(url_for('.login'))

    return render_template("mod_auth/signup.html", form=form)

def send_verification_mail(email, verification_code):

    from flask import current_app as app

    verification_url = app.config['ROOT_URL'] + '/verify'
    subject = "Please verify your email address for account activation."
    body = render_template('mod_auth/verification_mail.html', url=verification_url, email=email, verification_code=verification_code)
    print(send_simple_message(email, subject, str(body)))


@mod_auth.route('/login', methods=['GET', 'POST'])
def login():
    user_id = session.get('user_id', 0)
    g.user = Users.query.filter(Users.id == user_id).first()

    redirect_location = request.args.get('next', '')

    if g.user is not None:
        print(g.user.username)
        flash('Logged in as ' + g.user.username, 'success')
        if len(redirect_location) == 0:
            return redirect(url_for('.profile'))

        else:
            return redirect(url_for(redirect_location))

    form = LoginForm(request.form)

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and user.is_password_valid(form.password.data):
            if user.is_verified():
                session['user_id'] = user.id
                if len(redirect_location) == 0:
                    return redirect(url_for('.profile'))
                else:
                    return redirect(url_for(redirect_location))

            else:
                flash('Please verify your email and activate account first. Check your registered email.', 'error')
        else:
            flash('Wrong username or password', 'error')
        return redirect(url_for('.login'))

    return render_template("mod_auth/login.html", form=form, next=redirect_location)


@mod_auth.route('/verify/<string:email>/<string:verification_code>', methods=['GET', 'POST'])
def verify_account(email, verification_code):
    user = Users.query.filter_by(email=email).first()
    if user is not None:
        verification_status = user.verify(verification_code)
        db.session.add(user)
        db.session.commit()
    else:
        verification_status = 'fail'
    return render_template('mod_auth/verify.html', verification_status=verification_status)

@mod_auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    files = g.user.files
    return render_template("mod_auth/profile.html", user=g.user, files=files)

@mod_auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('.login'))
