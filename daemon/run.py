"""
ccextractor-web | run.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import sys
import os
import time
import subprocess
import config
import requests
import shutil

from parsers import ParseJob, ParseParameters, ParseCCExtractorParameters
from logger import Logger

logger = Logger(log_level=config.LOG_LEVEL,
                dir=config.LOG_FILE_DIR,
                filename="log")
log = logger.get_logger("daemon")

parameters = ParseParameters(sys.argv)


def get_cmd(job_config):
    video_file_path = parameters.job_dir + job_config.filename
    ccextractor_executable = parameters.ccextractor_binaries_dir + job_config.ccextractor_executable
    ccx_params = ParseCCExtractorParameters(job_config.parameters)

    ccx_params.params_list = [ccextractor_executable, video_file_path] + ccx_params.params_list
    ccx_params.params_list.extend(['-o', '{path}{name}.{output_file_extension}'.format(path=parameters.output_dir,
                                                                                       name=job_config.job_number,
                                                                                       output_file_extension=job_config.output_file_extension)])

    log.debug('Job: {job_no} >> CCX command : {cmd}".'.format(job_no=job_config.job_number, cmd=ccx_params.params_list))
    return ccx_params.params_list


def report_progress(job_config, status=None, return_code=None):
    payload = {'job_number': job_config.job_number,
               'token': job_config.token,
               'report_type': 'queue_status',
               'return_code': return_code,
               'status': status}
    return requests.post(parameters.report_url, data=payload)


def upload_log_file(job_config, filename, file_exist='yes'):
    payload = {'job_number': job_config.job_number,
               'token': job_config.token,
               'report_type': 'log',
               'file_exist': file_exist}
    files = {'file': open(filename, encoding='utf-8')}

    return requests.post(parameters.report_url, files=files, data=payload)


def upload_output_file(job_config, filename, file_exist='yes'):
    payload = {'job_number': job_config.job_number,
               'token': job_config.token,
               'report_type': 'output',
               'file_exist': file_exist}
    files = {'file': open(filename, encoding='utf-8')}
    return requests.post(parameters.report_url, files=files, data=payload)


while True:
    job_list = [f for f in os.listdir(parameters.job_dir) if f.endswith(".json")]
    job_list.sort()

    if job_list:
        job_config_file = parameters.job_dir + job_list[0]
        job_config = ParseJob(job_config_file)

        log.info('\n\nPicking Job: {job_no}'.format(job_no=job_config.job_number))
        log.debug('Job: {job_no} >> Setting status to "processing".'.format(job_no=job_config.job_number))
        rv = report_progress(job_config, 'processing')
        if rv.status_code is not 200:
            log.debug('Job: {job_no} >> Could not update status. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
        else:
            log.debug('Job: {job_no} >> Status set to "processing". Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))

        log.debug('Job: {job_no} >> Getting CCExtractor command".'.format(job_no=job_config.job_number))
        cmd = get_cmd(job_config)

        log_path = parameters.log_dir + job_config.job_number + config.LOG_FILE_EXTENSION

        try:
            log.debug('Job: {job_no} >> Creating log file : {log_path}".'.format(job_no=job_config.job_number, log_path=log_path))
            log.debug('Job: {job_no} >> Starting to process file.".'.format(job_no=job_config.job_number))

            with open(log_path, "w") as log_file:
                popen = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=log_file, universal_newlines=True)
                popen.communicate()
                log.info('Job: {job_no} >> Processing Complete. Return Code : {code}".'.format(job_no=job_config.job_number, code=popen.returncode))

        except FileNotFoundError:
            log.debug('Job: {job_no} >> Setting status to "missing_file".'.format(job_no=job_config.job_number))
            rv = report_progress(job_config, 'missing_file')
            if rv.status_code is not 200:
                log.debug('Job: {job_no} >> Could not update status. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
            else:
                log.debug('Job: {job_no} >> Status set to "missing_file". Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))

        except Exception as e:
            log.debug('Job: {job_no} >> Error occured while processing a file. Exception : {e}".'.format(job_no=job_config.job_number, e=e))
            log.info('Job: {job_no} >> Skipping job.".'.format(job_no=job_config.job_number))
            log.debug('Job: {job_no} >> Setting status to "error".'.format(job_no=job_config.job_number))
            rv = report_progress(job_config, 'error')
            if rv.status_code is not 200:
                log.debug('Job: {job_no} >> Could not update status. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
            else:
                log.debug('Job: {job_no} >> Status set to "error". Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))

            # TODO: https://github.com/CCExtractor/ccextractor/blob/f37829bb46e046d8914bb2a42937020add5d84bc/src/lib_ccx/ccx_common_common.h#L13

        else:
            log.info('Job: {job_no} >> Processing complete.'.format(job_no=job_config.job_number))
            log.debug('Job: {job_no} >> Setting status to "completed".'.format(job_no=job_config.job_number))
            rv = report_progress(job_config, 'completed', popen.returncode)
            if rv.status_code is not 200:
                log.debug('Job: {job_no} >> Could not update status. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
            else:
                log.debug('Job: {job_no} >> Status set to "completed". Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))

        if os.path.exists(log_path):
            log.info('Job: {job_no} >> Uploading logfile.'.format(job_no=job_config.job_number))
            rv = upload_log_file(job_config, log_path)
            if rv.status_code is not 200:
                log.debug('Job: {job_no} >> Could not upload logfile. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
            else:
                log.debug('Job: {job_no} >> logfile uploaded. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
        else:
            log.debug('Job: {job_no} >> Could not upload logfile - does not exist.'.format(job_no=job_config.job_number))
            rv = upload_log_file(job_config=job_config, filename=log_path, file_exist='no')
            if rv.status_code is not 200:
                log.debug('Job: {job_no} >> Could not upload logfile status. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
            else:
                log.debug('Job: {job_no} >> logfile status uploaded. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))

        output_file = '{path}{name}.{output_file_extension}'.format(path=parameters.output_dir,
                                                                    name=job_config.job_number,
                                                                    output_file_extension=job_config.output_file_extension)

        if os.path.exists(output_file):
            log.info('Job: {job_no} >> Uploading output file.'.format(job_no=job_config.job_number))
            rv = upload_output_file(job_config, output_file)
            if rv.status_code is not 200:
                log.debug('Job: {job_no} >> Could not upload output file. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
            else:
                log.debug('Job: {job_no} >> Output file uploaded. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
        else:
            log.debug('Job: {job_no} >> Could not upload output file - does not exist.'.format(job_no=job_config.job_number))
            rv = upload_log_file(job_config=job_config, filename=log_path, file_exist='no')
            if rv.status_code is not 200:
                log.debug('Job: {job_no} >> Could not upload output file status. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))
            else:
                log.debug('Job: {job_no} >> Output file status uploaded. Response Code : {code}".'.format(job_no=job_config.job_number, code=rv.status_code))

        log.debug('Job: {job_no} >> Archiving jobfile.'.format(job_no=job_config.job_number))
        shutil.copy(job_config_file, parameters.archive_dir)

        log.debug('Job: {job_no} >> Deleting job file and video file.'.format(job_no=job_config.job_number))
        if os.path.exists(job_config_file):
            os.remove(job_config_file)

        video_file_path = parameters.job_dir + job_config.filename
        if os.path.exists(output_file):
            os.remove(video_file_path)

    else:
        log.info('Ready to process next job.')
        time.sleep(config.RETRY_TIME)
