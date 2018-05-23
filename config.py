class Config(object):
    """
    Common configurations
    """

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
