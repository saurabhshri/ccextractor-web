"""
ccextractor-web | logger.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import logging
import os


class Logger:
    def __init__(self, log_level, dir, filename, format=None, console_level="", file_level=""):
        if not console_level:
            console_level = log_level
        if not file_level:
            file_level = log_level

        self.log_level = logging.getLevelName(log_level)
        self.console_level = logging.getLevelName(console_level)
        self.file_level = logging.getLevelName(file_level)

        if format is None:
            format = '[%(asctime)s] [%(name)s] [%(levelname)s] [%(pathname)s#L%(lineno)d]\t| "%(message)s"'
        format = logging.Formatter(format)

        self.log_to_console = logging.StreamHandler()
        self.log_to_console.setFormatter(format)
        self.log_to_console.setLevel(logging.getLevelName(self.console_level))

        path = os.path.join(dir, '{name}.log'.format(name=filename))
        self.log_to_file = logging.FileHandler(path)
        self.log_to_file.setFormatter(format)
        self.log_to_file.setLevel(self.file_level)

    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        logger.addHandler(self.log_to_console)
        logger.addHandler(self.log_to_file)
        return logger
