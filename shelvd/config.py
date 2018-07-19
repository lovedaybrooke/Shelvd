import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'bananarama'
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/shelvd"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(object):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/shelvd_testing'
    SQLALCHEMY_TRACK_MODIFICATIONS = False