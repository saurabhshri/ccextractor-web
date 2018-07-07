"""
ccextractor-web | controller.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import os
import shutil
import json
import hashlib
import collections
from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response, g, send_from_directory
from mod_dashboard.models import UploadedFiles, ProcessQueue, CCExtractorVersions, Platforms
from mod_dashboard.forms import UploadForm, NewCCExtractorVersionForm, NewJobForm
from mod_auth.models import Users, AccountType
from mod_auth.controller import login_required, check_account_type
from werkzeug import secure_filename
from database import db

mod_dashboard = Blueprint("mod_dashboard", __name__)


BUF_SIZE = 65536  # reading file in 64kb chunks

@mod_dashboard.route('/report_progress', methods=['GET', 'POST'])
def progress():
    from flask import current_app as app

    #Resp = collections.namedtuple('Resp', ['stat', 'reason'])
    job_number = request.form['job_number']
    queued_file = ProcessQueue.query.filter(ProcessQueue.id == job_number).first()
    if queued_file is not None:
        if request.form['token'] == queued_file.token:

            if request.form['report_type'] == 'queue_status':
                queued_file.status = request.form['status']
                db.session.add(queued_file)
                db.session.commit()
                #return Resp(stat='success', reason='')


            elif request.form['report_type'] == 'log':
                uploaded_file = request.files['file']
                if uploaded_file:
                    filename = secure_filename(uploaded_file.filename)
                    temp_path = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], filename)
                    uploaded_file.save(temp_path)
                    shutil.move(temp_path, os.path.join(app.config['LOGS_DIR']))
                #return Resp(stat='success', reason='')


            elif request.form['report_type'] == 'output':
                uploaded_file = request.files['file']
                if uploaded_file:
                    filename = secure_filename(uploaded_file.filename)
                    temp_path = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], filename)
                    uploaded_file.save(temp_path)
                    shutil.move(temp_path, os.path.join(app.config['OUTPUT_DIR']))
                #return Resp(stat='success', reason='')


        else:
            return "Invalid Token"
            #return Resp(stat='failed', reason='Invalid token')

    return "Invalid Request"
    #return Resp(stat='failed', reason='Invalid request')

@mod_dashboard.route('/new/<filename>', methods=['GET', 'POST'])
@login_required
def new_job(filename):
    file = UploadedFiles.query.filter(UploadedFiles.filename==filename).first()
    if file is not None:
        users_with_file_access = Users.query.filter(Users.files.any(id=file.id)).all()
        if g.user in users_with_file_access:
            form = NewJobForm()
            ccextractor = CCExtractorVersions.query.all()
            form.ccextractor_version.choices = [(str(cc.id), str(cc.version)) for cc in ccextractor]
            form.parameters.choices = [(str(cc.id), str(cc.version)) for cc in ccextractor]
            form.platforms.choices = [(str(p.value), str(Platforms(p.value).name)) for p in Platforms]

            # TODO:Process parameters before adding to queue
            paramters = form.parameters.data

            if form.validate_on_submit():
                rv = add_file_to_queue(added_by_user=g.user.id,
                                       filename=file.filename,
                                       ccextractor_version=form.ccextractor_version.data,
                                       platform=form.platforms.data,
                                       parameters=paramters,
                                       remarks=form.remark.data)

                if rv['status'] == 'duplicate':
                    flash('Job with same conifguration already in the queue. Job #{job_number}'.format(
                        job_number=rv['job_number']), 'warning')
                elif rv['status'] == 'failed':
                    flash('Failed to add job! Reason : {reason}'.format(reason=rv['reason']), 'error')
                else:
                    flash('Job added to queue. Job #{job_number}'.format(job_number=rv['job_number']), 'success')
            else:
                return render_template('mod_dashboard/newjob.html', filename=filename, form=form)
        else:
            flash('Invalid new job request!', 'error')
    else:
        flash('Invalid new job request!', 'error')
    return redirect(url_for('mod_dashboard.dashboard'))

@mod_dashboard.route('/upload', methods=['GET', 'POST'])
@mod_dashboard.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
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

                #TODO: Process video to get media info and store in an xml file

                os.rename(temp_path, os.path.join(app.config['VIDEO_REPOSITORY'], file_db.filename))
                flash('File uploaded.', 'success')


            file = UploadedFiles.query.filter(UploadedFiles.hash == file_hash).first()

            #TODO:Process parameters before adding to queue
            paramters = form.parameters.data
            if form.start_processing.data is True:
                rv = add_file_to_queue(added_by_user=g.user.id,
                                  filename=file.filename,
                                  ccextractor_version=form.ccextractor_version.data,
                                  platform=form.platforms.data,
                                  parameters=paramters,
                                  remarks=form.remark.data)

                if rv['status'] == 'duplicate':
                    flash('Job with same conifguration already in the queue. Job #{job_number}'.format(job_number=rv['job_number']), 'warning')
                elif rv['status'] == 'failed':
                    flash('Failed to add job! Reason : {reason}'.format(reason=rv['reason']), 'error')
                else:
                    flash('Job added to queue. Job #{job_number}'.format(job_number=rv['job_number']), 'success')

    queued_files = ProcessQueue.query.filter(ProcessQueue.added_by_user == g.user.id).all()
    uploaded_files = g.user.files
    return render_template('mod_dashboard/dashboard.html', form=form, accept=form.accept, queued_files=queued_files, uploaded_files=uploaded_files)

@mod_dashboard.route('/admin', methods=['GET', 'POST'])
@mod_dashboard.route('/admin-dashboard', methods=['GET', 'POST'])
@login_required
@check_account_type(account_types=[AccountType.admin])
def admin():
    ccextractor_form = NewCCExtractorVersionForm()
    if ccextractor_form.validate_on_submit():
        ccextractor = CCExtractorVersions.query.filter(CCExtractorVersions.commit == ccextractor_form.commit.data).first()
        if ccextractor is not None:
            flash('CCExtractor version with the commit already exists.', 'error')

        else:
            ccextractor = CCExtractorVersions(ccextractor_form.version.data, ccextractor_form.commit.data, ccextractor_form.linux_executable_path.data, ccextractor_form.windows_executable_path.data, ccextractor_form.mac_executable_path.data)
            db.session.add(ccextractor)
            db.session.commit()
            flash('CCExtractor version added!', 'success')

    ccextractor = CCExtractorVersions.query.order_by(db.desc(CCExtractorVersions.id)).all()
    queue = ProcessQueue.query.order_by(db.desc(ProcessQueue.id)).all()
    users = Users.query.order_by(db.desc(Users.id)).all()
    return render_template('mod_dashboard/ccextractor.html', type='new', ccextractor_form=ccextractor_form, ccextractor=ccextractor, queue=queue, users=users)

@mod_dashboard.route('/serve/<type>/<job_no>/<view>', methods=['GET', 'POST'])
@mod_dashboard.route('/serve/<type>/<job_no>', methods=['GET', 'POST'])
@login_required
def serve(type, job_no, view=None):
    from flask import current_app as app

    job = ProcessQueue.query.filter(ProcessQueue.id == job_no).first()
    if job is not None:
        if job.added_by_user == g.user.id:
            if type == 'log':
                return serve_file_download(file_name='{id}.log'.format(id=job.id), folder=app.config['LOGS_DIR'], as_attachment=(True if view is None else False))
            if type is 'output':
                return serve_file_download(file_name='{id}.{extension}'.format(id=job.id, extension=job.get_output_extension()), folder=app.config['OUTPUT_DIR'], as_attachment=(True if view is None else False))

    flash('Illegal request.', 'error')
    return redirect(request.referrer)

def serve_file_download(file_name, folder='', as_attachment=True, content_type='application/octet-stream'):

    return send_from_directory(os.path.join(folder, ''), file_name, as_attachment=as_attachment)

    """
    file_path = os.path.join(folder, file_name)
    print(file_path)
    print(os.path.getsize(file_path))
    response = make_response()
    response.headers['Content-Description'] = 'File Transfer'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = content_type
    response.headers['Content-Disposition'] = 'attachment; filename={file_name}'.format(file_name=file_name)
    response.headers['Content-Length'] = os.path.getsize(file_path)
    response.headers['X-Accel-Redirect'] = '/' + os.path.join('media-download', folder, file_name)
    print(response.headers)
    return response
    """

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
    from flask import current_app as app
    queued_file = ProcessQueue.query.filter((ProcessQueue.filename == filename) &
                                            (ProcessQueue.added_by_user == added_by_user) &
                                            (ProcessQueue.platform == platform) &
                                            (ProcessQueue.parameters == parameters) &
                                            (ProcessQueue.ccexractor_version == ccextractor_version)).first()
    if queued_file is None:
        queued_file = ProcessQueue(added_by_user, filename, ccextractor_version, platform, parameters, remarks)
        db.session.add(queued_file)
        db.session.commit()

        job_file_path = app.config['JOBS_DIR'] + str(queued_file.id) + '.json'

        ccextractor = CCExtractorVersions.query.filter(CCExtractorVersions.id == ccextractor_version).first()

        queue_dict = { 'job_number': str(queued_file.id),
                       'filename': filename,
                       'parameters': parameters,
                       'token': queued_file.token,
                       'platform': platform,
                       'executable_path': ccextractor.linux_executable_path
        }

        video_file_path = app.config['VIDEO_REPOSITORY'] + filename
        if os.path.exists(video_file_path):
            rc = shutil.copy(video_file_path, app.config['JOBS_DIR'])
            with open(job_file_path, 'w', encoding='utf8') as job_file:
                content = json.dumps(queue_dict, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                job_file.write(content)

            return {'status': 'success', 'job_number': queued_file.id}
        else:
            return {'status': 'failed', 'reason': 'file does not exist on server'}
    else:
        return {'status': 'duplicate', 'job_number': queued_file.id}
