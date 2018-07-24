import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PLIVO_AUTH_ID = os.environ['PLIVO_AUTH_ID']
    PLIVO_AUTH_TOKEN = os.environ['PLIVO_AUTH_TOKEN']
    RECIPIENT_NUMBER = os.environ['RECIPIENT_NUMBER']
    SENDING_NUMBER = os.environ['SENDING_NUMBER']
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_ASSOCIATE_TAG = os.environ['AWS_ASSOCIATE_TAG']


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/shelvd_testing'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
