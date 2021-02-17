import os
basedir = os.path.abspath(os.path.dirname(__file__))


# Creates the configuration class.
class Config:
#################################### ACTION ####################################
# Configure .env file and determine backup values.
# Determine additional configuration variables, if required.
# ADMIN EMAIL ADDRESS must be created, and this is the mail sender.
################################################################################
    SECRET_KEY = os.environ.get("SECRET_KEY",'temporary')
    APP_ADMIN = os.environ.get("APP_ADMIN",'')
    MAIL_SERVER = os.environ.get("MAIL_SERVER", 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT','587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS','true').lower() in \
        ['true','on','1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PREFIX = os.environ.get('MAIL_PREFIX','hunnydu - ')
    MAIL_SENDER = 'hunnydu Admin <hunnydu.io>'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POST_PER_PAGE = 20
    COMMENT_PER_PAGE = 50
    FLASK_FOLLOWERS_PER_PAGE = 50
    CHROME_DRIVER_URI = os.path.join(basedir,'venv/chromedriver')
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.5
    SSL_REDIRECT = False

    @staticmethod
    def init_app(app):
        pass


# Create the debug configuration.
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL',
        'sqlite:///'+ os.path.join(basedir,'data-dev.sqlite'))


# Create the testing configuration.
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL',
        'sqlite://')
    WTF_CSRF_ENABLED = False


# Create the production configuration.
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        'sqlite:///'+ os.path.join(basedir,'data.sqlite'))
    SSL_REDIRECT = True

    # Provide for error logging.
    @classmethod
    def init_app(cls,app):
        Config.init_app(app)

        # Email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls,'MAIL_USERNAME',None) is not None:
            credentials = (cls.MAIL_USERNAME,cls.MAIL_PASSWORD)
            if getattr(cls,'MAIL_USE_TLS',None):
                secure()
        mail_handler = SMTPHandler(
            mailhost = (cls.MAIL_SERVER,cls.MAIL_PORT),
            fromaddr = cls.MAIL_SENDER,
            toaddrs = [cls.APP_ADMIN],
            subject = cls.MAIL_PREFIX + ' Application Error',
            credentials = credentials,
            secure = secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


# Create the Heroku configuration.
class HerokuConfig(ProductionConfig):
    SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls,app):
        ProductionConfig.init_app(app)

        # Configure for proxy server interaction.
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


# Create the linux configuration.
class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls,app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


# Determine which configuration to load.
config = {
    'development':DevelopmentConfig(),
    'testing':TestingConfig(),
    'production':ProductionConfig(),
    'heroku':HerokuConfig(),
    'unix':UnixConfig(),

    'default':DevelopmentConfig()
}
