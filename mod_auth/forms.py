"""
ccextractor-web | mod_auth/forms.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

Based on https://github.com/CCExtractor/sample-platform/blob/master/mod_auth/forms.py
"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, ValidationError


def valid_password(form, field):
    from flask import current_app as app
    min_pwd_len = app.config['MIN_PWD_LEN']
    max_pwd_len = app.config['MAX_PWD_LEN']
    pass_size = len(field.data)
    if pass_size == 0:
        raise ValidationError('The password can not be empty!')
    if pass_size < min_pwd_len or pass_size > max_pwd_len:
        raise ValidationError(
            'Password needs to be between {min_pwd_len} and {max_pwd_len} characters long (you entered {char})'.format
            (min_pwd_len=min_pwd_len, max_pwd_len=max_pwd_len, char=pass_size)
        )


class SignupEmailForm(FlaskForm):
    email = EmailField('Email', [DataRequired(message='Email address is not filled in.'),
                                 Email(message='Entered value is not a valid email address.')])
    submit = SubmitField('Register')


class SignupForm(FlaskForm):
    name = StringField('Name', [DataRequired(message='Name is not filled in.')])
    password = PasswordField('Password', [DataRequired(message='Password is not filled in.'), valid_password])
    password_repeat = PasswordField('Repeat password', [DataRequired(message='Repeated password is not filled in.')])
    submit = SubmitField('Complete Signup.')

    @staticmethod
    def validate_password_repeat(form, field):
        if field.data != form.password.data:
            raise ValidationError('The password needs to match the new password.')


class LoginForm(FlaskForm):
    email = EmailField('Email', [DataRequired(message='Email address is not filled in.'),
                                 Email(message='Entered value is not a valid email address.')])
    password = PasswordField('Password', [DataRequired(message='Password cannot be empty.')])
    submit = SubmitField('Login')
