"""
ccextractor-web | mod_auth/models.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import enum
import pytz

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from tzlocal import get_localzone

from database import db


class AccountType(enum.Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"
    bot = "bot"


file_access = db.Table('file_access',
                       db.Column('file_id', db.Integer, db.ForeignKey('uploaded_files.id')),
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
                       )


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(70))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.Enum(AccountType))
    files = db.relationship('UploadedFiles', secondary='file_access', backref=db.backref('user', lazy='dynamic'), order_by='UploadedFiles.id')
    sign_up_timestamp = db.Column(db.DateTime(timezone=True))

    def __init__(self, email, password, username=None, name=None, account_type=AccountType.user, sign_up_timestamp=None):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.account_type = account_type

        if username is None:
            self.username = generate_username(email)
        else:
            self.username = username

        tz = get_localzone()

        if sign_up_timestamp is None:
            sign_up_timestamp = tz.localize(datetime.now(), is_dst=None)
            sign_up_timestamp = sign_up_timestamp.astimezone(pytz.UTC)

        if sign_up_timestamp.tzinfo is None:
            sign_up_timestamp = pytz.utc.localize(sign_up_timestamp, is_dst=None)

        self.sign_up_timestamp = sign_up_timestamp

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

    @db.reconstructor
    def may_the_timezone_be_with_it(self):
        """
        Localize the timestamp to utc
        """
        self.sign_up_timestamp = pytz.utc.localize(self.sign_up_timestamp, is_dst=None)


def generate_username(email):
    # TODO : Disallow a set of usernames such as 'admin'
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
