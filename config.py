class Config(object):
    """
    Common configurations
    """
    CONFIG_READING_TEST = "May the 24th be with you!"
    TEMP_UPLOAD_FOLDER = "files/"
    MIN_PWD_LEN = 8
    MAX_PWD_LEN = 128

    # Put any configurations here that are common across all environments

class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True

class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

class LocalServerConfig(Config):
    """
    Local server instance configurations
    """

    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'local': LocalServerConfig
}
