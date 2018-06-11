"""
ccextractor-web | mod_auth/controller.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g, abort
from email_validator import validate_email, EmailNotValidError

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
    received_email_address = form.email.data
    if form.validate_on_submit():
        try:
            v = validate_email(received_email_address)
            email = v["email"]  # replace with normalized forms
            user = Users.query.filter_by(email=form.email.data).first()
            if user is None:

                user = Users(username=generate_username(email), email=email, password=form.password.data,
                             name=form.name.data)
                db.session.add(user)
                db.session.commit()
                flash('Signup Complete! Please Login!', 'success')

            else:
                flash('Email is already registered!', 'error')

            return redirect(url_for('.login'))

        except EmailNotValidError as e:
            flash('Entered value is not a valid email address. ' + str(e), 'error')

    return render_template("mod_auth/signup.html", form=form)

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
            session['user_id'] = user.id
            if len(redirect_location) == 0:
                return redirect(url_for('.profile'))
            else:
                return redirect(url_for(redirect_location))

        flash('Wrong username or password', 'error')

    return render_template("mod_auth/login.html", form=form, next=redirect_location)

@mod_auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id', 0)
    g.user = Users.query.filter(Users.id == user_id).first()
    return render_template("mod_auth/profile.html", user=g.user)

@mod_auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('.login'))
