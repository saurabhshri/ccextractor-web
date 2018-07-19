"""
ccextractor-web | logger.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""

import logging
import os


class Logger:
    def __init__(self, log_level, dir, filename):
        self.log_level = logging.getLevelName(log_level)
        format = logging.Formatter('[%(asctime)s] [%(levelname)s] | %(message)s | [file : %(pathname)s#L%(lineno)d] > [function: %(funcName)s]')

        self.log_to_console = logging.StreamHandler()
        self.log_to_console.setFormatter(format)
        self.log_to_console.setLevel(self.log_level)

        path = os.path.join(dir, '{name}.log'.format(name=filename))
        self.log_to_file = logging.FileHandler(path)
        self.log_to_file.setFormatter(format)
        self.log_to_file.setLevel(self.log_level)

    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        logger.addHandler(self.log_to_console)
        logger.addHandler(self.log_to_file)
        return logger
