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

from flask import Blueprint, render_template, request, flash, redirect, url_for, g, send_from_directory

from mod_dashboard.models import UploadedFiles, ProcessQueue, CCExtractorVersions, Platforms, CCExtractorParameters, DetailsForTemplate
from mod_dashboard.forms import UploadForm, NewCCExtractorVersionForm, NewJobForm, NewCCExtractorParameterForm
from mod_auth.models import Users, AccountType
from mod_auth.controller import login_required, check_account_type
from werkzeug.utils import secure_filename

from database import db
from template import LayoutHelper

mod_dashboard = Blueprint("mod_dashboard", __name__)


BUF_SIZE = 65536  # reading file in 64kb chunks


@mod_dashboard.route('/upload', methods=['GET', 'POST'])
@mod_dashboard.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    from flask import current_app as app
    from run import log
    ccextractor = CCExtractorVersions.query.all()
    form = UploadForm()
    form.ccextractor_version.choices = [(str(cc.id), str(cc.version)) for cc in ccextractor]
    form.platforms.choices = [(str(p.value), str(Platforms(p.value).name)) for p in Platforms]
    if form.validate_on_submit():
        uploaded_file = request.files[form.file.name]
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            temp_path = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], filename)
            uploaded_file.save(temp_path)
            log.debug('Saving as temporary file : {path} by user: {user_id}'.format(path=temp_path, user_id=g.user.id))

            if app.config['ENABLE_MEDIAINFO_SUPPORT']:
                from pymediainfo import MediaInfo
                log.debug('Checking if file is vaild : {path} by user: {user_id}'.format(path=temp_path, user_id=g.user.id))

                if app.config['MEDIAINFO_LIB_PATH']:
                    media_info = MediaInfo.parse(filename=temp_path, library_file=app.config['MEDIAINFO_LIB_PATH'])
                else:
                    media_info = MediaInfo.parse(filename=temp_path)

                media_info_json = json.loads(media_info.to_json())

                is_valid_video_file = False
                for track in media_info.tracks:
                    if track.track_type == 'Video':
                        is_valid_video_file = True
                        break

                if not is_valid_video_file:
                    log.warning('Invalid file : {path} uploaded by user: {user_id}'.format(path=temp_path, user_id=g.user.id))
                    flash('Invalid file uploaded, No video track found.', 'error')
                    return redirect(url_for('mod_dashboard.dashboard'))

            file_hash = create_file_hash(temp_path)

            if file_exist(file_hash):
                file = UploadedFiles.query.filter(UploadedFiles.hash == file_hash).first()
                users_with_file_access = Users.query.filter(Users.files.any(id=file.id)).all()
                if g.user not in users_with_file_access:
                    file.user.append(g.user)
                    db.session.commit()
                    flash('File with same hash already uploaded, the file has been made available to you for processing in your dashboard.', 'warning')
                    log.debug('File with the hash already exist. Original uploader: {og_uploader}. Access granted to user: {user_id}'.format(og_uploader=file.original_uploader, user_id=g.user.id))
                else:
                    flash('File already uploaded by you. If you want to re-process it(say, with different parameters, head to your dashboard', 'warning')
                    log.debug('Duplicate file : {file} uploaded by user: {user_id}'.format(file=file.id, user_id=g.user.id))

                os.remove(temp_path)
                log.debug('Deleting temporary file : {path}'.format(path=temp_path))

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

                # TODO: Process video to get media info and store in an xml file

                os.rename(temp_path, os.path.join(app.config['VIDEO_REPOSITORY'], file_db.filename))
                log.debug('File moved to video repository : {path}'.format(path=os.path.join(app.config['VIDEO_REPOSITORY'], file_db.filename)))

                if app.config['ENABLE_MEDIAINFO_SUPPORT']:
                    media_info_file_path = os.path.join(app.config['VIDEO_REPOSITORY'], '{filename}{extension}'.format(filename=file_db.hash, extension='.json'))
                    try:
                        log.debug('Creating mediainfo file for the video : {name} | {file_path}'.format(name=file_db.filename, file_path=media_info_file_path))
                        with open(media_info_file_path, 'w', encoding='utf8') as media_info_file:
                            content = json.dumps(media_info_json, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                            media_info_file.write(content)
                            log.debug('Created media info file : {file_path}'.format(file_path=media_info_file_path))
                    except Exception as e:
                        log.error('Error creating media info file : {file_path} | {e}'.format(file_path=media_info_file_path, e=e))

                flash('File uploaded.', 'success')
                log.debug('File {file_id} uploaded by: {user_id}'.format(file_id=file_db.id, user_id=g.user.id))

            file = UploadedFiles.query.filter(UploadedFiles.hash == file_hash).first()

            # TODO:Process parameters before adding to queue
            resp = json.loads(parse_ccextractor_parameters(form.parameters.data))
            if resp['status'] == 'success':
                parameters = json.dumps(resp['parameters'])
                if form.start_processing.data is True:
                    rv = add_file_to_queue(added_by_user=g.user.id,
                                           filename=file.filename,
                                           ccextractor_version=form.ccextractor_version.data,
                                           platform=form.platforms.data,
                                           parameters=parameters,
                                           remarks=form.remark.data,
                                           output_file_extension=resp['output_file_extension'])

                    if rv['status'] == 'duplicate':
                        flash('Job with same conifguration already in the queue. Job #{job_number}'.format(job_number=rv['job_number']), 'warning')
                    elif rv['status'] == 'failed':
                        flash('Failed to add job! Reason : {reason}'.format(reason=rv['reason']), 'error')
                    else:
                        flash('Job added to queue. Job #{job_number}'.format(job_number=rv['job_number']), 'success')
        return redirect(url_for('mod_dashboard.dashboard'))

    details = DetailsForTemplate(g.user.id)
    layout = LayoutHelper(logged_in=True, details=details)
    return render_template('mod_dashboard/dashboard.html',
                           form=form,
                           layout=layout.get_entries(),
                           details=details)


@mod_dashboard.route('/dashboard/new/<filename>', methods=['GET', 'POST'])
@login_required
def new_job(filename):
    from run import log
    file = UploadedFiles.query.filter(UploadedFiles.filename == filename).first()
    if file is not None:
        users_with_file_access = Users.query.filter(Users.files.any(id=file.id)).all()
        if g.user in users_with_file_access:
            form = NewJobForm()
            ccextractor = CCExtractorVersions.query.all()
            form.ccextractor_version.choices = [(str(cc.id), str(cc.version)) for cc in ccextractor]
            form.platforms.choices = [(str(p.value), str(Platforms(p.value).name)) for p in Platforms]

            if form.validate_on_submit():
                # TODO:Process parameters before adding to queue
                resp = json.loads(parse_ccextractor_parameters(form.parameters.data))
                if resp['status'] == 'success':
                    parameters = json.dumps(resp['parameters'])
                    rv = add_file_to_queue(added_by_user=g.user.id,
                                           filename=file.filename,
                                           ccextractor_version=form.ccextractor_version.data,
                                           platform=form.platforms.data,
                                           parameters=parameters,
                                           remarks=form.remark.data,
                                           output_file_extension=resp['output_file_extension'])

                    if rv['status'] == 'duplicate':
                        flash('Job with same conifguration already in the queue. Job #{job_number}'.format(job_number=rv['job_number']), 'warning')
                        log.warning('Duplicate job configuration for job number: {job_number} '.format(job_number=rv['job_number']))

                    elif rv['status'] == 'failed':
                        flash('Failed to add job! Reason : {reason}'.format(reason=rv['reason']), 'error')
                        log.error('Failed to add job! Reason : {reason}'.format(reason=rv['reason']))

                    else:
                        flash('Job added to queue. Job #{job_number}'.format(job_number=rv['job_number']), 'success')
                        log.debug('Job added to queue. Job #{job_number}'.format(job_number=rv['job_number']))
            else:
                details = DetailsForTemplate(g.user.id)
                layout = LayoutHelper(logged_in=True, details=details)
                return render_template('mod_dashboard/new_job.html',
                                       file=file,
                                       form=form,
                                       layout=layout.get_entries(),
                                       details=details)
        else:
            flash('Invalid new job request!', 'error')
    else:
        flash('Invalid new job request!', 'error')
    return redirect(url_for('mod_dashboard.dashboard'))


@mod_dashboard.route('/admin-dashboard', methods=['GET', 'POST'])
@login_required
@check_account_type(account_types=[AccountType.admin])
def admin():
    from run import log
    ccextractor_form = NewCCExtractorVersionForm()
    ccextractor_parameters_form = NewCCExtractorParameterForm()
    if ccextractor_form.validate_on_submit() and ccextractor_form.submit.data:
        ccextractor = CCExtractorVersions.query.filter(CCExtractorVersions.commit == ccextractor_form.commit.data).first()
        if ccextractor is not None:
            flash('CCExtractor version with the commit already exists.', 'error')

        else:
            ccextractor = CCExtractorVersions(ccextractor_form.version.data, ccextractor_form.commit.data, ccextractor_form.linux_executable_path.data, ccextractor_form.windows_executable_path.data, ccextractor_form.mac_executable_path.data)
            db.session.add(ccextractor)
            db.session.commit()
            flash('CCExtractor version added!', 'success')
            log.debug('New CCExtractor version added. [{ccx}]'.format(ccx=ccextractor.id))

    if ccextractor_parameters_form.validate_on_submit() and ccextractor_parameters_form.submit.data:
        parameter = CCExtractorParameters.query.filter(CCExtractorParameters.parameter == ccextractor_parameters_form.parameter.data).first()
        if parameter is not None:
            flash('CCExtractor parameter with the commit already exists. Id = {id}'.format(id=parameter.id), 'error')
        else:
            parameter = CCExtractorParameters(ccextractor_parameters_form.parameter.data,
                                              ccextractor_parameters_form.description.data,
                                              ccextractor_parameters_form.requires_value.data,
                                              ccextractor_parameters_form.enabled.data)
            db.session.add(parameter)
            db.session.commit()
            update_cmd_json(parameter, "new")
            log.debug('New CCExtractor parameter added. [{ccx}]'.format(ccx=parameter.id))
            flash('CCExtractor parameter added!', 'success')

    details = DetailsForTemplate(g.user.id, admin_dashboard=True)
    layout = LayoutHelper(logged_in=True, details=details)
    return render_template('mod_dashboard/dashboard.html',
                           layout=layout.get_entries(),
                           details=details,
                           ccextractor_parameters_form=ccextractor_parameters_form,
                           ccextractor_form=ccextractor_form)


@mod_dashboard.route('/dashboard/files', methods=['GET', 'POST'])
@login_required
def uploaded_files():
    details = DetailsForTemplate(g.user.id)
    layout = LayoutHelper(logged_in=True, details=details)
    return render_template('mod_dashboard/uploaded-files.html', layout=layout.get_entries(), details=details)


@mod_dashboard.route('/dashboard/queue', methods=['GET', 'POST'])
@login_required
def user_queue():
    details = DetailsForTemplate(g.user.id)
    layout = LayoutHelper(logged_in=True, details=details)
    return render_template('mod_dashboard/queue.html', layout=layout.get_entries(), details=details)


@mod_dashboard.route('/admin-dashboard/files', methods=['GET', 'POST'])
@login_required
@check_account_type(account_types=[AccountType.admin])
def admin_uploaded_files():
    details = DetailsForTemplate(g.user.id, admin_dashboard=True)
    layout = LayoutHelper(logged_in=True, details=details)
    return render_template('mod_dashboard/uploaded-files.html', layout=layout.get_entries(), details=details)


@mod_dashboard.route('/admin-dashboard/queue', methods=['GET', 'POST'])
@login_required
@check_account_type(account_types=[AccountType.admin])
def admin_queue():
    details = DetailsForTemplate(g.user.id, admin_dashboard=True)
    layout = LayoutHelper(logged_in=True, details=details)
    return render_template('mod_dashboard/queue.html', layout=layout.get_entries(), details=details)


@mod_dashboard.route('/admin-dashboard/users', methods=['GET', 'POST'])
@login_required
@check_account_type(account_types=[AccountType.admin])
def user_list():
    details = DetailsForTemplate(g.user.id, admin_dashboard=True)
    layout = LayoutHelper(logged_in=True, details=details)
    return render_template('mod_dashboard/user-list.html', layout=layout.get_entries(), details=details)


@mod_dashboard.route('/change-acc-type/<user_id>/<type>', methods=['GET', 'POST'])
@login_required
@check_account_type(account_types=[AccountType.admin])
def change_acc_type(user_id, type):
    user = Users.query.filter(Users.id == user_id).first()
    if user is not None:
        if type == 'admin':
            user.account_type = AccountType.admin
        elif type == 'user':
            user.account_type = AccountType.user
        db.session.commit()
        flash('Account type change successful.', 'success')
    else:
        flash('User not found.', 'error')

    return redirect(request.referrer)


@mod_dashboard.route('/serve/<type>/<job_no>', methods=['GET', 'POST'])
@mod_dashboard.route('/serve/<type>/<job_no>/<view>', methods=['GET', 'POST'])
@login_required
def serve(type, job_no, view=None):
    from flask import current_app as app
    from run import log
    job = ProcessQueue.query.filter(ProcessQueue.id == job_no).first()
    if job is not None:
        if job.added_by_user == g.user.id or g.user.account_type == AccountType.admin:
            if type == 'log':
                log.debug('Serving log file for job number: {job_no} to user : {user_id}'.format(job_no=job_no, user_id=g.user.id))
                return serve_file_download(file_name='{id}.log'.format(id=job.id), folder=app.config['LOGS_DIR'], as_attachment=(True if view is None else False))
            elif type == 'output':
                log.debug('Serving output file for job number: {job_no} to user : {user_id}'.format(job_no=job_no, user_id=g.user.id))
                return serve_file_download(file_name='{id}.{extension}'.format(id=job.id, extension=job.get_output_extension()), folder=app.config['OUTPUT_DIR'], as_attachment=(True if view is None else False))
            else:
                flash('Invalid filetype.', 'error')
        else:
            log.warning('Forbidden download request for: {job_no} by user : {user_id}'.format(job_no=job_no, user_id=g.user.id))
            flash('Forbidden.', 'error')
    else:
        log.warning('Invalid download request for: {job_no} by user : {user_id}'.format(job_no=job_no, user_id=g.user.id))
        flash('Illegal request. Job not found', 'error')
    return redirect(request.referrer)


@mod_dashboard.route('/delete/<filename>', methods=['GET', 'POST'])
@login_required
def delete(filename):
    from flask import current_app as app
    from run import log
    file = UploadedFiles.query.filter(UploadedFiles.filename == filename).first()
    if file is not None:
        users_with_file_access = Users.query.filter(Users.files.any(id=file.id)).all()
        if g.user in users_with_file_access:
            if len(users_with_file_access) > 1:
                log.debug('Access tp file: {file_id} revoked for user : {user_id}'.format(file_id=file.id, user_id=g.user.id))
                file.user.remove(g.user)
            else:
                video_file_path = os.path.join(app.config['VIDEO_REPOSITORY'], filename)
                if os.path.exists(video_file_path):
                    os.remove(video_file_path)
                    log.debug('File: {file_id} deleted by user : {user_id}'.format(file_id=file.id, user_id=g.user.id))
                db.session.delete(file)
            db.session.commit()
            flash('{filename} deleted.'.format(filename=filename), 'success')
        else:
            log.debug('Forbidden delete request for file: {file_id} by user : {user_id}'.format(file_id=file.id, user_id=g.user.id))
            flash('Forbidden.'.format(filename=filename), 'error')
    else:
        log.debug('Invalid delete request for file: {filename} by user : {user_id}'.format(filename=filename, user_id=g.user.id))
        flash('{filename} not found.'.format(filename=filename), 'error')
    return redirect(request.referrer)


@mod_dashboard.route('/parameters/<function>/<id>', methods=['GET', 'POST'])
@login_required
@check_account_type(account_types=[AccountType.admin])
def manage_parameter(function, id):
    from run import log
    parameter = CCExtractorParameters.query.filter(CCExtractorParameters.id == id).first()
    if parameter is not None:
        if function == 'toggle':
            parameter.toggle_enable()
            db.session.commit()
            update_cmd_json(parameter, 'update')
            flash('Enable status toggled!', 'success')
            log.debug('Toggled enable status for parameter: {param_id} by user : {user_id}'.format(param_id=parameter.id, user_id=g.user.id))

            """
            enabled = "False"
            if parameter.enabled:
                enabled = "True"
            return json.dumps({'status': 'success', 'enabled': enabled}, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
            """

        elif function == "delete":
            db.session.delete(parameter)
            db.session.commit()
            update_cmd_json(parameter, 'delete')
            flash('Parameter deleted!', 'success')
            log.debug('Deleted parameter: {param_id} by user : {user_id}'.format(param_id=parameter.id, user_id=g.user.id))

        return redirect(request.referrer)

    log.debug('Invalid parameter manipulation request: {function} for parameter:{parameter_id} by user: {user_id}'.format(function=function, param_id=id, user_id=g.user.id))
    return json.dumps({'status': 'failed'}, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)


@mod_dashboard.route('/report_progress', methods=['GET', 'POST'])
def progress():
    from flask import current_app as app
    from run import log
    job_number = request.form['job_number']
    queued_file = ProcessQueue.query.filter(ProcessQueue.id == job_number).first()
    if queued_file is not None:
        if request.form['token'] == queued_file.token:
            if request.form['report_type'] == 'queue_status':
                queued_file.status = request.form['status']
                db.session.add(queued_file)
                db.session.commit()
                log.debug('[Job Number: {queued_file_id}] > Updating status to [{status}].'.format(queued_file_id=queued_file.id, status=queued_file.status))
                resp = {'status': 'success'}
                return json.dumps(resp)

            elif request.form['report_type'] == 'log':
                uploaded_file = request.files['file']
                if uploaded_file:
                    filename = secure_filename(uploaded_file.filename)
                    temp_path = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], filename)
                    uploaded_file.save(temp_path)
                    shutil.move(temp_path, os.path.join(app.config['LOGS_DIR']))
                    log.debug('[Job Number: {queued_file_id}] > Uploaded log file : {filename}'.format(queued_file_id=queued_file.id, filename=filename))
                    resp = {'status': 'success'}
                else:
                    resp = {'status': 'failed', 'reason': 'No file found'}
                return json.dumps(resp)

            elif request.form['report_type'] == 'output':
                uploaded_file = request.files['file']
                if uploaded_file:
                    filename = secure_filename(uploaded_file.filename)
                    temp_path = os.path.join(app.config['TEMP_UPLOAD_FOLDER'], filename)
                    uploaded_file.save(temp_path)
                    shutil.move(temp_path, os.path.join(app.config['OUTPUT_DIR']))
                    log.debug('[Job Number: {queued_file_id}] > Uploaded Output file : {filename}'.format(queued_file_id=queued_file.id, filename=filename))
                    resp = {'status': 'success'}
                else:
                    resp = {'status': 'failed', 'reason': 'No file found'}
                return json.dumps(resp)
        else:
            log.error('[Job Number: {queued_file_id}] > Invalid token for progress report. Token : {token}'.format(queued_file_id=queued_file.id, token=request.form['token']))
            return "Invalid Token"

    log.error('Invalid request for progress report. Job No.: {job_no} Token : {token}'.format(job_no=job_number, token=request.form['token']))
    return "Invalid Request"


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


def update_cmd_json(parameter, type="new"):
    from flask import current_app as app
    from run import log
    cmd_json_file = os.path.join(app.config['COMMANDS_JSON_PATH'])

    with open(cmd_json_file) as cmd:
        commands = json.load(cmd)

    index = 0
    for param in commands['commands']:
        if parameter.parameter in param['parameter']:
            if type == 'new':
                flash('Parameter already exists in JSON file!', 'error')
                log.warning('Parameter: {param} already exists in JSON file'.format(param=param))
                return
            elif type == 'delete' or type == 'update':
                flash('Updating parameter in JSON file!', 'warning')
                del commands['commands'][index]
                log.debug('Removing parameter: {param} from JSON file'.format(param=param))

        index += 1

    if type != 'delete':
        new_command = {"data": parameter.parameter,
                       "value": parameter.parameter,
                       "parameter": parameter.parameter,
                       "description": parameter.description,
                       "requires_value": parameter.requires_value,
                       "enabled": parameter.enabled
                       }
        commands['commands'].append(new_command)
        log.debug('Adding parameter: {param} to JSON file'.format(param=parameter.parameter))

    with open("static/commands.json", 'w', encoding='utf-8') as cmd:
        json.dump(commands, cmd, indent=4, separators=(',', ': '), ensure_ascii=False)


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


def add_file_to_queue(added_by_user, filename, ccextractor_version, platform, parameters, remarks, output_file_extension='srt'):
    from flask import current_app as app
    from run import log
    queued_file = ProcessQueue.query.filter((ProcessQueue.filename == filename) &
                                            (ProcessQueue.added_by_user == added_by_user) &
                                            (ProcessQueue.platform == platform) &
                                            (ProcessQueue.parameters == parameters) &
                                            (ProcessQueue.ccexractor_version == ccextractor_version)).first()

    file = UploadedFiles.query.filter(UploadedFiles.filename == filename).first()
    if queued_file is None:
        queued_file = ProcessQueue(added_by_user=added_by_user,
                                   filename=filename,
                                   original_filename=file.original_name,
                                   ccextractor_version=ccextractor_version,
                                   platform=platform,
                                   parameters=parameters,
                                   remarks=remarks,
                                   output_file_extension=output_file_extension)
        db.session.add(queued_file)
        db.session.commit()

        log.debug('Job: {job_no} > Created by {user_id}.'.format(job_no=queued_file.id, user_id=added_by_user))
        log.debug('Job: {job_no} > Platform : {platform}.'.format(job_no=queued_file.id, platform=platform))

        if platform == Platforms.linux.value:
            job_dir = app.config['LINUX_JOBS_DIR']
        elif platform == Platforms.windows.value:
            job_dir = app.config['WINDOWS_JOBS_DIR']
        elif platform == Platforms.mac.value:
            job_dir = app.config['MAC_JOBS_DIR']

        job_file_path = os.path.join(job_dir, '{job_id}.json'.format(job_id=queued_file.id))
        name, extension = os.path.splitext(filename)
        video_file_name = '{job_id}{extension}'.format(job_id=queued_file.id, extension=extension)

        log.debug('Job: {job_no} > Job Directory : {job_dir}'.format(job_no=queued_file.id, job_dir=job_dir))
        log.debug('Job: {job_no} > Job File Path : {job_file}'.format(job_no=queued_file.id, job_file=job_file_path))

        ccextractor = CCExtractorVersions.query.filter(CCExtractorVersions.id == ccextractor_version).first()

        queue_dict = {'job_number': str(queued_file.id),
                      'filename': video_file_name,
                      'parameters': parameters,
                      'token': queued_file.token,
                      'platform': platform,
                      'executable_path': ccextractor.linux_executable_path,
                      'output_file_extension': queued_file.output_file_extension}

        video_file_path = os.path.join(app.config['VIDEO_REPOSITORY'], filename)
        if os.path.exists(video_file_path):
            try:
                job_video_file_path = os.path.join(job_dir, '{video_file_name}'.format(video_file_name=video_file_name))
                log.debug('Job: {job_no} > Copying video file to Jobs dir : {video_file_path} > {job_video_file_path}'.format(job_no=queued_file.id, video_file_path=video_file_path, job_video_file_path=job_video_file_path))
                shutil.copy(video_file_path, job_video_file_path)
                log.debug('Job: {job_no} > Video file copied.'.format(job_no=queued_file.id))

            except Exception as e:
                log.error('Job: {job_no} > Error Copying video file to Jobs dir. : {exception}'.format(job_no=queued_file.id, exception=e))
                return {'status': 'failed', 'reason': 'Unable to copy video file for processing.'}

            try:
                log.debug('Job: {job_no} > Creating job configuration file: {job_file_path}'.format(job_no=queued_file.id, job_file_path=job_file_path))
                with open(job_file_path, 'w', encoding='utf8') as job_file:
                    content = json.dumps(queue_dict, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                    job_file.write(content)
                    log.debug('Job: {job_no} > Created job configuration file: {job_file_path}'.format(job_no=queued_file.id, job_file_path=job_file_path))
            except Exception as e:
                log.error('Job: {job_no} > Error creating job configuration file. : {exception}'.format(job_no=queued_file.id, exception=e))
                return {'status': 'failed', 'reason': 'Unable to create job configuration file.'}

            return {'status': 'success', 'job_number': queued_file.id}
        else:
            return {'status': 'failed', 'reason': 'File does not exist on server.'}
    else:
        return {'status': 'duplicate', 'job_number': queued_file.id}


def parse_ccextractor_parameters(params):
    from flask import current_app as app
    params = params.split()
    cmd_json_file = os.path.join(app.config['COMMANDS_JSON_PATH'])

    with open(cmd_json_file) as cmd:
        commands = json.load(cmd)

    parameters = {}
    invalid_parameters = {}
    disabled_parameters = {}
    parameters_missing_values = {}

    param_count = 0
    is_value = False

    # TODO: Optimise the whole process, prepare lists and output extension while parsing
    for param in params:
        param_count += 1

        if is_value:
            is_value = False
            continue

        param_exist = False
        for command in commands['commands']:
            if param == command['parameter']:
                param_exist = True
                if command['requires_value']:
                    if param_count >= len(params):
                        entry = {'{parameter}'.format(parameter=command['parameter']): '{value}'.format(value="")}
                        parameters_missing_values.update(entry)
                        break
                    else:
                        entry = {'{parameter}'.format(parameter=command['parameter']): '{value}'.format(value=params[param_count])}
                        is_value = True
                else:
                    entry = {'{parameter}'.format(parameter=command['parameter']): '{value}'.format(value="")}

                if command['enabled']:
                    parameters.update(entry)
                else:
                    disabled_parameters.update(entry)
                break

        if not param_exist:
            entry = {'{parameter}'.format(parameter=param): '{value}'.format(value="")}
            invalid_parameters.update(entry)

    status = "success"
    if invalid_parameters or disabled_parameters or parameters_missing_values:
        status = "failed"

        if invalid_parameters:
            invalid_params_list = []
            for key, value in invalid_parameters.items():
                invalid_params_list.append(key)
            flash("Invalid Parameters + {invalid_params_list}".format(invalid_params_list=invalid_params_list), 'error')

        if disabled_parameters:
            disabled_params_list = []
            for key, value in disabled_parameters.items():
                disabled_params_list.append(key)
            flash("Disabled Parameters + {disabled_params_list}".format(disabled_params_list=disabled_params_list), 'error')

        if parameters_missing_values:
            parameters_missing_values_list = []
            for key, value in parameters_missing_values.items():
                parameters_missing_values_list.append(key)
            flash("Parameters missing values : + {parameters_missing_values_list}".format(parameters_missing_values_list=parameters_missing_values_list), 'error')

    output_file_extension = 'srt'
    for key, value in parameters.items():
        if "-out=" in key:
            output_file_extension = key[5:]

        elif key in ['-xml', '-srt', '-dvdraw', '-sami', '-smi', '-webvtt', '--transcript', '-txt', '--timedtranscript',
                     '-ttxt', '-null']:
            output_file_extension = key[1:]

    resp = {'status': status,
            'invalid_params': invalid_parameters,
            'disabled_params': disabled_parameters,
            'parameters_missing_values': parameters_missing_values,
            'parameters': parameters,
            'output_file_extension': output_file_extension
            }

    return json.dumps(resp)
