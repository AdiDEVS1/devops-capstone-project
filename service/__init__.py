"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import sys
from flask import Flask
from service import config
from service.common import log_handlers

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

# Import the routes After the Flask app is created
# pylint: disable=wrong-import-position, cyclic-import, wrong-import-order
from service import routes, models  # noqa: F401 E402

# pylint: disable=wrong-import-position
from service.common import error_handlers, cli_commands  # noqa: F401 E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    models.init_db(app)  # make our database tables
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("%s: Cannot continue", error)
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")

# ----------------------------------------------------------------------
# App factory for testing and reuse
# ----------------------------------------------------------------------
def create_app():
    """Create and configure a new Flask app instance"""
    flask_app = Flask(__name__)
    flask_app.config.from_object(config)

    # Re-imports for route setup
    from service import routes, models
    from service.common import error_handlers, cli_commands

    log_handlers.init_logging(flask_app, "gunicorn.error")

    try:
        models.init_db(flask_app)
    except Exception as error:  # pylint: disable=broad-except
        flask_app.logger.critical("%s: Cannot continue", error)
        sys.exit(4)

    return flask_app
