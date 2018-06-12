"""
ccextractor-web | mod_auth/models.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
import time
import hashlib
from tzlocal import get_localzone
from database import db

class AccountType(enum.Enum):
    admin = "admin",
    moderator = "moderator"
    user = "user"
    bot = "bot"

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(70))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.Enum(AccountType))
    files = db.relationship('Files', backref='uploader', lazy=True)
    sign_up_timestamp = db.Column(db.DateTime(timezone=True))
    verified = db.Column(db.Boolean, nullable=False)
    verification_code = db.Column(db.String(255), unique=True)

    def __init__(self, username, email, password, name = None, account_type = AccountType.user, sign_up_timestamp = None):
        self.name = name
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.account_type = account_type

        tz = get_localzone()

        if sign_up_timestamp is None:
            sign_up_timestamp = tz.localize(datetime.now(), is_dst=None)
            sign_up_timestamp = sign_up_timestamp.astimezone(pytz.UTC)

        if sign_up_timestamp.tzinfo is None:
            sign_up_timestamp = pytz.utc.localize(sign_up_timestamp, is_dst=None)

        self.sign_up_timestamp = sign_up_timestamp
        self.verified = False

        hash = hashlib.sha256()
        hash.update(('{email}{salt}'.format(email=email, salt=time.time().hex()).encode('utf-8')))

        self.verification_code = hash.hexdigest()

    def __repr__(self):
        return '<User {username}>'.format(username=self.username)


    """
    @property
    def password(self):
        raise AttributeError('Password can not be accessed directly!')

    @password.setter
    def password(self, new_password):
        self._password = generate_password_hash(new_password)

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, new_name):
        self._name = new_name


    @property
    def email(self):
        return self.email

    @email.setter
    def email(self, new_email):
        self._email = new_email

    @property
    def account_type(self):
        return self.account_type

    @account_type.setter
    def account_type(self, new_account_type):
        self._account_type = new_account_type
    """

    @property
    def is_admin(self):
        return self.account_type == AccountType.admin

    def is_password_valid(self, password):
        return check_password_hash(self.password, password)

    def has_role(self, account_type):
        return self.account_type == account_type or self.is_admin

    def is_verified(self):
        return self.verified

    def verify(self, verification_code):
        if verification_code == self.verification_code:
            if self.verified is True:
                return 'duplicate'
            else:
                self.verified = True
                return 'success'
        return 'fail'

    @db.reconstructor
    def may_the_timezone_be_with_it(self):
        """
        Localize the timestamp to utc
        """
        self.sign_up_timestamp = pytz.utc.localize(self.sign_up_timestamp, is_dst=None)
