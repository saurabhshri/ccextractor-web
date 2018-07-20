"""
ccextractor-web | config_parser.py.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import os
from werkzeug.utils import import_string
from config import app_config


def parse_config(obj):
    """
    Parses given config either from a file or from an object. Method borrowed from https://github.com/CCExtractor/sample-platform/blob/master/config_parser.py#L4.

    :param obj: The config to parse.
    :type obj: any
    :return: A dictionary containing the parsed Flask config
    :rtype: dict
    """
    config = {}
    if isinstance(obj, str):
        obj = import_string(obj)
    for key in dir(obj):
        if key.isupper():
            config[key] = getattr(obj, key)

    return config


# creating configuration : set FLASK_ENV as 'development' / 'production' / 'local'
configuration_environment = os.environ.get('FLASK_ENV', 'development')

if configuration_environment not in app_config:
    configuration_environment = "development"

general_config = parse_config(app_config[configuration_environment])
