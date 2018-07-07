"""
ccextractor-web | parsers.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import json
import argparse

class ParseJob():
    def __init__(self, job_number):
        self.job_config = {}

        with open(job_number, 'r', encoding="utf-8") as f:
            self.job_config = json.load(f)

        self.ccextractor_executable = self.job_config['executable_path']
        self.filename = self.job_config['filename']
        self.job_number = self.job_config['job_number']
        self.parameters = self.job_config['parameters']
        self.platform = self.job_config['platform']
        self.token = self.job_config['token']

    def get_job_config(self):
        return self.job_config

class ParseParameters():
    def __init__(self, argv):
        self.paramters = {}

        while argv:
            if argv[0][0] == '-':
                self.paramters[argv[0]] = argv[1]
            argv = argv[1:]

        self.job_dir = self.paramters['-jobDir']
        self.output_dir = self.paramters['-outputDir']
        self.archive_dir = self.paramters['-archiveDir']
        self.ccextractor_binaries_dir = self.paramters['-ccextractorBinariesDir']
        self.log_dir = self.paramters['-logDir']
        self.report_url = self.paramters['-reportURL']

    def get_raw_parameters(self):
        return self.paramters
