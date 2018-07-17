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
import json
import shutil
from parsers import ParseJob, ParseParameters, ParseCCExtractorParameters

parameters = ParseParameters(sys.argv)

def get_cmd(job_config):
    video_file_path = parameters.job_dir + job_config.filename
    ccextractor_executable = parameters.ccextractor_binaries_dir + job_config.ccextractor_executable
    ccx_params = ParseCCExtractorParameters(job_config.parameters)

    params_list = [ccextractor_executable, video_file_path]
    params_list.extend(ccx_params.params_list)
    params_list.extend(['-o', '{path}{name}.{output_file_extension}'.format(path=parameters.output_dir, name=job_config.job_number, output_file_extension=ccx_params.output_file_extension)])

    print(params_list)

    #TODO: srt -> params.output_format
    return params_list

def report_progress(job_config, status = None, return_code = None):
    payload = {'job_number': job_config.job_number,
               'token': job_config.token,
               'report_type': 'queue_status',
               'return_code': return_code,
               'status': status}
    return requests.post(parameters.report_url, data=payload)

def upload_log_file(job_config, filename):
    payload = {'job_number': job_config.job_number,
               'token': job_config.token,
               'report_type': 'log'}
    files = {'file': open(filename, encoding='utf-8')}

    return requests.post(parameters.report_url, files=files, data=payload)

def upload_output_file(job_config, filename):
    payload = {'job_number': job_config.job_number,
               'token': job_config.token,
               'report_type': 'output'}
    files = {'file': open(filename, encoding='utf-8')}
    return requests.post(parameters.report_url, files=files, data=payload)

while True:
    job_list = [f for f in os.listdir(parameters.job_dir) if f.endswith(".json")]
    job_list.sort()

    if job_list:
        job_config_file = parameters.job_dir + job_list[0]
        job_config = ParseJob(job_config_file)

        print("\n\nJob #" + job_config.job_number)

        rv = report_progress(job_config, 'processing')
        print("Setting status to 'processing' , response : " + str(rv))

        cmd = get_cmd(job_config)

        log_path = parameters.log_dir + job_config.job_number + config.LOG_FILE_EXTENSION

        try:
            with open(log_path, "w") as log_file:
                popen = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=log_file, universal_newlines=True)
                popen.communicate()
                print("Processing complete , return code : " + str(popen.returncode))

            # TODO: https://github.com/CCExtractor/ccextractor/blob/f37829bb46e046d8914bb2a42937020add5d84bc/src/lib_ccx/ccx_common_common.h#L13

            rv = report_progress(job_config, 'completed', popen.returncode)
            print("Setting status to 'completed' , response : " + str(rv))

            video_file_path = parameters.job_dir + job_config.filename
            os.remove(video_file_path)

        except FileNotFoundError:
            rv = report_progress(job_config, 'missing_file')
            print("Setting status to 'missing_file' , response : " + str(rv))

        except Exception as e:
            print(e)
            #skipping for now
            rv = report_progress(job_config, 'error')
            print("Setting status to 'error' , response : " + str(rv))

        shutil.copy(job_config_file, parameters.archive_dir)
        os.remove(job_config_file)

        upload_log_file(job_config, log_path)

        # TODO: srt -> params.output_format
        output_file = '{path}/{name}.srt'.format(path=parameters.output_dir, name=job_config.job_number)
        upload_output_file(job_config, output_file)

    else:
        time.sleep(config.RETRY_TIME)
