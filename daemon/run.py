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
from parsers import ParseJob, ParseParameters

parameters = ParseParameters(sys.argv)

def get_cmd(job_config):
    video_file_path = parameters.job_dir + job_config.filename
    ccextractor_executable = parameters.ccextractor_binaries_dir + job_config.ccextractor_executable
    params = job_config.parameters

    return [ccextractor_executable, video_file_path] #, params]

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
               'report_type' : 'log'}
    files = {'file': open(filename)}

    return requests.post(parameters.report_url, files=files, data=payload)

def upload_output_file(job_config, filename):
    payload = {'job_number': job_config.job_number,
               'token': job_config.token,
               'report_type': 'output',
               'status': status}
    return requests.post(parameters.report_url, files=files, data=json.dumps(payload))

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
            shutil.copy(job_config_file, parameters.archive_dir)
            os.remove(job_config_file)

        except Exception as e:
            print(e)
            #skipping for now
            shutil.copy(job_config_file, parameters.archive_dir)
            os.remove(job_config_file)

        upload_log_file(job_config, log_path)



    else:
        time.sleep(config.RETRY_TIME)






