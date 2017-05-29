# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~
"""
from os.path import abspath, dirname, join

class BaseConfiguration:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'Bf2AUBwH090O0NMcyCWuUzEBbwBZL2Kn7c8elzNK3IpqjM8paf'
    BASE_DIR = abspath(dirname(__file__))
    MYSQL_CONNECTOR_FORMAT = 'mysql+mysqlconnector://{user}:{password}' \
    '@{host}:{port}/{db}'
    SQLALCHEMY_DATABASE_URI = MYSQL_CONNECTOR_FORMAT.format(
        user='',
        password='',
        host='',
        port='',
        db=''
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_POOL_SIZE = 1
    # SQLALCHEMY_MAX_OVERFLOW = 0
    REST_API_VERSION_URL_PREFIX = '/rest/v0.1'      # 버전 관리
    UPLOAD_DIR = join(BASE_DIR, 'uploads')
    GCM_KEY = 'AIzaSyCEfhK7yWQj39LW6E3N_dw5uO1f_BdPMzg'
    FCM_API_KEY = 'AIzaSyBxrziBdRu-EhySObCxFCPuEnYBsVzfsvU'

class DebugConfiguration(BaseConfiguration):
    DEBUG = True
    BASE_DIR = BaseConfiguration.BASE_DIR
    SQLALCHEMY_DATABASE_URI = BaseConfiguration.MYSQL_CONNECTOR_FORMAT.format(
        user='midas2017',
        password='midas2017',
        host='localhost',
        port='3306',
        db='midas2017'
    )
    # SQLALCHEMY_ECHO = True
    # UPLOAD_DIR = join(BASE_DIR, 'test-uploads')

class TestConfiguration(DebugConfiguration):
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'