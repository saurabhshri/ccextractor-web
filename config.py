"""
ccextractor-web | config.py

This is a general config file containing variables required for functioning of the application. Each config variable is
accompanied by the description and sample values are already filled in. Make sure to replace them with your own values
before deploying the application.

The secret config file is present in the `instance` directory.
"""


class Config(object):
    """
    This class contains the common configurations across all the app environments (Production/Development/Local).
    """

    """
        Name:       ROOT_URL
        Summary:    Enter the root url (domain) of the application. This will serve as the base URL. All the app
                    endpoints routes will be with respect to this, including mail links.
        Required:   Yes
        Tip:        Do not append '/' at the end of the URL.
    """
    ROOT_URL = "http://127.0.0.1:5000"

    """
        Name:       CONFIG_READING_TEST
        Summary:    This value is used in one of the tests, leave it as it is.
        Required:   Yes
    """
    CONFIG_READING_TEST = "May the 24th be with you!"

    """
        Name:       COMMANDS_JSON_PATH
        Summary:    Enter the path to the JSON file which contains the CCExtractor parameter.
        Required:   Yes
        Tip:        Default and recommended path is "static/commands.json"
    """
    COMMANDS_JSON_PATH = "static/commands.json"

    """
        Name:       MIN_PWD_LEN
                    MAX_PWD_LEN = 128
        Summary:    Enter the minimum and maximum password length the app should use.
        Required:   Yes
    """
    MIN_PWD_LEN = 8
    MAX_PWD_LEN = 128

    """
        Name:       LOG_LEVEL
        Summary:    Set the log level to be used.
        Required:   Yes
        Tip:        Possible Values - CRITICAL ERROR WARNING INFO DEBUG
    """
    LOG_LEVEL = "DEBUG"

    """
        Name:       LOG_FILE_DIR
        Summary:    Enter the path to the directory where the application logs are stored.
        Required:   Yes
        Tip:        If full path is not provided, it'll use the path relative to the application root directory.
    """
    LOG_FILE_DIR = "logs/"

    """
        Name:       ENABLE_MEDIAINFO_SUPPORT
        Summary:    If MediaInfo support is enabled, the file is validated using mediainfo as additonal layer and a json
                    file with complete information is stored in video repository folder with {filename}.json
        Required:   Yes
        Tip:        Set it to either True or False. Recommended to set True.
    """
    ENABLE_MEDIAINFO_SUPPORT = True

    """
        Name:       MEDIAINFO_LIB_PATH
        Summary:    Set the path to libmediainfo and the app will use it. Leave empty to try to find it automatically.
        Required:   Only if ENABLE_MEDIAINFO_SUPPORT = True
    """
    MEDIAINFO_LIB_PATH = "/usr/local/lib/libmediainfo.dylib"


class DevelopmentConfig(Config):
    """
    This class contains the sepcific configuration for Development environment along with common configuration.
    """

    DEBUG = True


class ProductionConfig(Config):
    """
    This class contains the sepcific configuration for Production environment along with common configuration.
    """

    DEBUG = False


class LocalServerConfig(Config):
    """
    This class contains the sepcific configuration for Local environment along with common configuration.
    """

    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'local': LocalServerConfig
}
