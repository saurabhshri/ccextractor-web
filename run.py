import sys

# 3rd party imports
from flask import Flask

# modules and internal imports
from config import app_config
from landing.controller import landing

#creating Flask app object
app = Flask(__name__, instance_relative_config=True)


# Registering blueprint for all modules
app.register_blueprint(landing)

#creating configuration : pass 'development' or 'production' as parameter while running app
def createConfig():

    if len(sys.argv) > 1:
        configuration_environment = sys.argv[1]
    else:
        configuration_environment = "development"

    if configuration_environment not in app_config:
        print("Invalid Configuration, Possible Values : development/production")
        exit(-1)

    app.config.from_object(app_config[configuration_environment])
    app.config.from_pyfile('config.py') # secret configurations


if __name__ == '__main__':
    createConfig()
    app.run()
