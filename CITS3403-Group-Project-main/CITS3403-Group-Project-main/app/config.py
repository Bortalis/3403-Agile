import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

# config class
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# production config
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

# test config
class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory'