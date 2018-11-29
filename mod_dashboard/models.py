"""
ccextractor-web | models.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import enum
import pytz

from flask import url_for
from datetime import datetime
from tzlocal import get_localzone

from database import db

from mod_auth.controller import generate_verification_code
from mod_auth.models import Users, AccountType


class ProcessStauts(enum.Enum):
    pending = 'pending'
    processing = 'processing'
    completed = 'completed'
    error = 'error'
    missing_file = 'file not found'


class Platforms(enum.Enum):
    linux = 'linux'
    windows = 'windows'
    mac = 'mac'


class UploadedFiles(db.Model):
    __tablename__ = 'uploaded_files'
    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.Text(), nullable=False)
    extension = db.Column(db.String(64), nullable=False)
    hash = db.Column(db.String(128), unique=True)
    filename = db.Column(db.String(140), nullable=False)
    size = db.Column(db.String(20))
    original_uploader = db.Column(db.Integer, nullable=False)
    upload_timestamp = db.Column(db.DateTime(timezone=True))

    def __init__(self, original_name, hash, original_uploader, extension='', size='', upload_timestamp=None):
        self.original_name = original_name
        self.hash = hash
        self.extension = extension
        self.original_uploader = original_uploader
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
        return '<UploadedFile {id}>'.format(id=self.id)

    @db.reconstructor
    def may_the_timezone_be_with_it(self):
        """
        Localize the timestamp to utc
        """
        self.upload_timestamp = pytz.utc.localize(self.upload_timestamp, is_dst=None)


class ProcessQueue(db.Model):
    __tablename__ = 'process_queue'
    id = db.Column(db.Integer, primary_key=True)
    added_by_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.Text(), nullable=False)
    filename = db.Column(db.String(140), nullable=False)
    ccexractor_version = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.Enum(Platforms))
    parameters = db.Column(db.Text())
    output_file_extension = db.Column(db.String(10))
    remarks = db.Column(db.Text())
    queue_timestamp = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.Enum(ProcessStauts))
    token = db.Column(db.String(128), unique=True)

    def __init__(self, added_by_user, filename, original_filename=None, ccextractor_version=None, platform=Platforms.linux, parameters=None, remarks=None, status=ProcessStauts.pending, output_file_extension='srt', queue_timestamp=None):
        self.added_by_user = added_by_user
        self.filename = filename
        self.original_filename = original_filename
        self.parameters = parameters
        self.remarks = remarks
        self.status = status
        self.platform = platform
        self.output_file_extension = output_file_extension

        tz = get_localzone()

        if queue_timestamp is None:
            queue_timestamp = tz.localize(datetime.now(), is_dst=None)
            queue_timestamp = queue_timestamp.astimezone(pytz.UTC)

        if queue_timestamp.tzinfo is None:
            queue_timestamp = pytz.utc.localize(queue_timestamp, is_dst=None)

        self.queue_timestamp = queue_timestamp

        if ccextractor_version is None:
            if platform is Platforms.linux:
                ccextractor_version = CCExtractorVersions.query.filter(CCExtractorVersions.linux_executable_path is not None).order_by('-id').first()
            elif platform is Platforms.windows:
                ccextractor_version = CCExtractorVersions.query.filter(CCExtractorVersions.windows_executable_path is not None).order_by('-id').first()
            else:
                ccextractor_version = CCExtractorVersions.query.filter(CCExtractorVersions.mac_executable_path is not None).order_by('-id').first()
            self.ccexractor_version = ccextractor_version.version
        else:
            self.ccexractor_version = ccextractor_version

        token = '{id}{timestamp}'.format(id=self.id, timestamp=self.queue_timestamp)

        self.token = generate_verification_code(token)

    def __repr__(self):
        return '<ProcessQueue {id}>'.format(id=self.id)

    def get_output_extension(self):
        return self.output_file_extension

    @db.reconstructor
    def may_the_timezone_be_with_it(self):
        """
        Localize the timestamp to utc
        """
        self.queue_timestamp = pytz.utc.localize(self.queue_timestamp, is_dst=None)


class CCExtractorVersions(db.Model):
    __tablename__ = 'ccextractor_versions'
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(100), nullable=False)
    commit = db.Column(db.String(64), nullable=False)
    linux_executable_path = db.Column(db.Text())
    windows_executable_path = db.Column(db.Text())
    mac_executable_path = db.Column(db.Text())

    def __init__(self, version, commit, linux_executable_path=None, windows_executable_path=None, mac_executable_path=None):
        self.version = version
        self.commit = commit
        self.linux_executable_path = linux_executable_path
        self.windows_executable_path = windows_executable_path
        self.mac_executable_path = mac_executable_path

    def __repr__(self):
        return '<CExtractorVersion {id}>'.format(id=self.id)


class CCExtractorParameters(db.Model):
    __tablename__ = 'ccextractor_parameters'
    id = db.Column(db.Integer, primary_key=True)
    parameter = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text())
    requires_value = db.Column(db.Boolean())
    enabled = db.Column(db.Boolean())

    def __init__(self, parameter, description, requires_value=False, enabled=True):
        self.parameter = parameter
        self.description = description
        self.requires_value = requires_value
        self.enabled = enabled

    def toggle_enable(self):
        self.enabled = not self.enabled

    def __repr__(self):
        return '<CExtractorParamter {id}>'.format(id=self.id)


class DetailsForTemplate():
    def __init__(self, user_id, admin_dashboard=False):

        self.user = Users.query.filter(Users.id == user_id).first()
        self.admin_dashboard = admin_dashboard

        from flask import current_app as app
        self.kvm_enabled = app.config['ENABLE_KVM']

        if self.kvm_enabled:
            from mod_kvm.models import KVM
            self.kvm = KVM.query.all()

        if self.user.account_type == AccountType.admin:
            self.admin_dashboard_url = url_for('mod_dashboard.admin')
            self.user_dashboard_url = url_for('mod_dashboard.dashboard')

        if admin_dashboard:
            self.dashboard_url = url_for('mod_dashboard.admin')
            self.uploaded_files_url = url_for('mod_dashboard.admin_uploaded_files')
            self.queue_url = url_for('mod_dashboard.admin_queue')
            self.user_list_url = url_for('mod_dashboard.user_list')
            self.queue = ProcessQueue.query.order_by(db.desc(ProcessQueue.id)).all()
            self.users = Users.query.order_by(db.desc(Users.id)).all()
            self.uploaded_files = UploadedFiles.query.order_by(db.desc(UploadedFiles.id)).all()
            self.ccextractor_versions = CCExtractorVersions.query.order_by(db.desc(CCExtractorVersions.id)).all()
            self.ccextractor_parameters = CCExtractorParameters.query.order_by(db.desc(CCExtractorParameters.id)).all()
            self.queued_files = ProcessQueue.query.filter((ProcessQueue.status == ProcessStauts.pending)).order_by(db.desc(ProcessQueue.id)).all()
            self.processed_files = ProcessQueue.query.filter((ProcessQueue.status == ProcessStauts.completed)).order_by(db.desc(ProcessQueue.id)).all()
            self.errored_files = ProcessQueue.query.filter((ProcessQueue.status == ProcessStauts.error)).order_by(db.desc(ProcessQueue.id)).all()

        else:
            self.dashboard_url = url_for('mod_dashboard.dashboard')
            self.uploaded_files_url = url_for('mod_dashboard.uploaded_files')
            self.queue_url = url_for('mod_dashboard.user_queue')
            self.queued_files = ProcessQueue.query.filter((ProcessQueue.added_by_user == user_id) & (ProcessQueue.status == ProcessStauts.pending)).order_by(db.desc(ProcessQueue.id)).all()
            self.processed_files = ProcessQueue.query.filter((ProcessQueue.added_by_user == user_id) & (ProcessQueue.status == ProcessStauts.completed)).order_by(db.desc(ProcessQueue.id)).all()
            self.errored_files = ProcessQueue.query.filter((ProcessQueue.added_by_user == user_id) & (ProcessQueue.status == ProcessStauts.error)).order_by(db.desc(ProcessQueue.id)).all()
            self.queue = ProcessQueue.query.filter(ProcessQueue.added_by_user == user_id).order_by(db.desc(ProcessQueue.id)).all()
            self.uploaded_files = self.user.files
