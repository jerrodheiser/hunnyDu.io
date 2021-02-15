from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

# Create Bootstrap object for styling.
bootstrap = Bootstrap()

# Create mail object for email.
mail = Mail()

# Create moment object for time.
moment = Moment()

# Create db object.
db = SQLAlchemy()

# Create login manager object to manage logins.
login_manager = LoginManager()

login_manager.login_view = 'auth.login'

# Create pagdown object.
pagedown = PageDown()

# App factory.
def create_app(config_name):
    app = Flask(__name__,static_folder="../build", static_url_path='/')
    app.config.from_object(config[config_name])

    # Initialize the objects in the app context.
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # Import and register blueprints.
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')


    # Return the app context created.
    return app
