import os

class Config(object):
    """shared configurations"""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

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
