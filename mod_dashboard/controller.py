"""
ccextractor-web | controller.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import os
import hashlib
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
from mod_dashboard.models import UploadedFiles, ProcessQueue, CCExtractorVersions, Platforms
from mod_dashboard.forms import UploadForm
from mod_auth.controller import login_required
from mod_auth.models import Users
from werkzeug import secure_filename
from database import db

mod_dashboard = Blueprint("mod_dashboard", __name__)


BUF_SIZE = 65536  # reading file in 64kb chunks

@mod_dashboard.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    from flask import current_app as app
    ccextractor = CCExtractorVersions.query.all()
    form = UploadForm()
    form.ccextractor_version.choices = [(str(cc.id), str(cc.version)) for cc in ccextractor]
    form.parameters.choices = [(str(cc.id), str(cc.version)) for cc in ccextractor]
    form.platforms.choices = [(str(p.value), str(Platforms(p.value).name)) for p in Platforms]
    if form.validate_on_submit():
        uploaded_file = request.files[form.file.name]
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            temp_path = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], filename)
            uploaded_file.save(temp_path)
            file_hash = create_file_hash(temp_path)
            if file_exist(file_hash):
                file = UploadedFiles.query.filter(UploadedFiles.hash == file_hash).first()
                users_with_file_access = Users.query.filter(Users.files.any(id=file.id)).all()
                if g.user not in users_with_file_access:
                    file.user.append(g.user)
                    db.session.commit()
                    flash(
                        'File with same hash already uploaded, the file has been made available to you for processing in your dashboard.',
                        'warning')
                else:
                    flash('File already uploaded by you. If you want to re-process it(say, with different parameters, head to your dashboard',
                        'warning')
                os.remove(temp_path)
            else:
                size = os.path.getsize(temp_path)
                filename, extension = os.path.splitext(filename)
                file_db = UploadedFiles(original_name=filename,
                                hash=file_hash,
                                original_uploader=g.user.id,
                                extension=extension,
                                size=size)
                db.session.add(file_db)
                db.session.commit()
                file_db.user.append(g.user)
                db.session.commit()
                os.rename(temp_path, os.path.join(app.config['TEMP_UPLOAD_FOLDER'], file_db.filename))
                flash('File uploaded.', 'success')


            file = UploadedFiles.query.filter(UploadedFiles.hash == file_hash).first()

            if form.start_processing.data is True:
                rv = add_file_to_queue(added_by_user=g.user.id,
                                  filename=file.filename,
                                  ccextractor_version=form.ccextractor_version.data,
                                  platform=form.platforms.data,
                                  parameters=form.parameters.data,
                                  remarks=form.remark.data)

                if rv['status'] == 'duplicate':
                    flash('Job with same conifguration already in the queue. Job #{job_number}'.format(job_number=rv['job_number']), 'warning')
                else:
                    flash('Job added to queue. Job #{job_number}'.format(job_number=rv['job_number']), 'success')

    return render_template('mod_dashboard/upload.html', form=form, accept=form.accept)

def create_file_hash(path):
    hash = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            hash.update(data)
    return hash.hexdigest()

def file_exist(file_hash):
    file = UploadedFiles.query.filter(UploadedFiles.hash == file_hash).first()
    if file is None:
        return False
    else:
        return True

def add_file_to_queue(added_by_user, filename, ccextractor_version, platform, parameters, remarks):
    queued_file = ProcessQueue.query.filter((ProcessQueue.filename == filename) &
                                            (ProcessQueue.added_by_user == added_by_user) &
                                            (ProcessQueue.platform == platform) &
                                            (ProcessQueue.parameters == parameters) &
                                            (ProcessQueue.ccexractor_version == ccextractor_version)).first()
    if queued_file is None:
        queued_file = ProcessQueue(added_by_user, filename, ccextractor_version, platform, parameters, remarks)
        db.session.add(queued_file)
        db.session.commit()
        return {'status': 'success', 'job_number': queued_file.id}
    else:
        return {'status': 'duplicate', 'job_number': queued_file.id }
