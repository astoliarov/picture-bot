# coding: utf-8

import os

BASEDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

DEBUG = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_EXPIRE_ON_COMMIT = False

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

SECRET_KEY = 'not-so-secret'

STORAGE_DIR = 'storage'

MARKER = ''
FACEBOOK_APP_TOKEN = ''
FACEBOOK_APP_SECRET = ''

IMGUR_STATE = ''
IMGUR_CLIENT_ID = ''
IMGUR_CLIENT_SECRET = ''

ENCRYPTED_INFO_MAX_AGE = 60 * 60 * 12  # 12 hours

URL = ''
