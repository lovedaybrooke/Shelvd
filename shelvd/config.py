import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RECIPIENT_NUMBER = os.environ.get('RECIPIENT_NUMBER')
    SENDING_NUMBER = os.environ.get('SENDING_NUMBER')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_ASSOCIATE_TAG = os.environ.get('AWS_ASSOCIATE_TAG')


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/shelvd_testing'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
