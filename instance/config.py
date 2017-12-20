import os

class Config(object):
    """shared configurations"""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    MAIL_SERVER = 'nbo2.domainskenya.co.ke'
    MAIL_PORT = '465'
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    APP_URL = os.getenv('APP_URL')

class DevelopmentConfig(Config):
    """development configrations"""
    DEBUG = True

class TestingConfig(Config):
    """Configurations for Testing, with its own database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql:///apitest_db"
    DEBUG = True


class ProductionConfig(Config):
    """production configurations."""
    DEBUG = False
    TESTING = False

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
