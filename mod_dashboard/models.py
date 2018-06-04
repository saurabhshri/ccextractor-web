"""
ccextractor-web | models.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54@gmail.com
Link     : https://github.com/saurabhshr

"""
from database import db

from datetime import datetime
import pytz
from tzlocal import get_localzone


class Files(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.Text(), nullable=False)
    extension = db.Column(db.String(64), nullable=False)
    hash = db.Column(db.String(128), unique=True)
    filename = db.Column(db.String(140), nullable=False)
    size = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('Users', uselist=False)
    upload_timestamp = db.Column(db.DateTime(timezone=True))
    parameters = db.Column(db.Text(), nullable=False)
    remark = db.Column(db.Text(), nullable=False)

    def __init__(self, original_name, hash, user_id, extension='', size='', parameters='', remark='', upload_timestamp=None):
        self.original_name = original_name
        self.hash = hash
        self.extension = extension
        self.user_id = user_id
        self.parameters = parameters
        self.remark = remark
        self.size = size

        tz = get_localzone()

        if upload_timestamp is None:
            upload_timestamp = tz.localize(datetime.now(), is_dst=None)
            upload_timestamp = upload_timestamp.astimezone(pytz.UTC)

        if upload_timestamp.tzinfo is None:
            upload_timestamp = pytz.utc.localize(upload_timestamp, is_dst=None)

        self.upload_timestamp = upload_timestamp

        self.filename = hash + extension

    def __repr__(self):
        return '<Upload {id}>'.format(id=self.id)
