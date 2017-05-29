# -*- coding: utf-8 -*-
"""
    main.constants
    ~~~~~~~~~~~~~~~~~~~

    상수 관리
"""

class LoginType:
    """로그인 타입
    """
    EMAIL = 'email'
    FACEBOOK = 'facebook'

class ErrorCode:
    """HTTP 에러 코드
    """
    NOT_FOUND = 'NOT_FOUND'
    NOT_FOUND_USER = 'NOT_FOUND_USER'
    METHOD_NOT_ALLOWED = 'METHOD_NOT_ALLOWED'
    INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'
    INVALID_DATA_ERROR = 'INVALID_DATA_ERROR'
    DATABASE_ERROR = 'DATABASE_ERROR'
    AUTH_ERROR = 'AUTH_ERROR'
    SERVICE_AREA_NOT_SUPPORTED_ERROR = \
    'SERVICE_AREA_NOT_SUPPORTED_ERROR'
    CHECK_IN_ERROR = 'CHECK_IN_ERROR'
    AUTO_CHECK_OUT = 'AUTO_CHECK_OUT'
    NO_PROFILE = 'NO_PROFILE'
    NOT_REGISTERED_PUSH_TOKEN = 'NOT_REGISTERED_PUSH_TOKEN'
    REQUEST_TIMEOUT = 'REQUEST_TIMEOUT'


class GCMType:
    NOTE = 'note'
    CHECK_OUT = 'check_out'
    UPDATE_LOCATION = 'update_location'
    UPDATE_CHECK_IN = 'update_check_in'
    UPDATE_CHECK_OUT = 'update_check_out'
    UPDATE_NEWS_FEED = 'update_news_feed'
    UNREGISTRATION = 'unregistration'
    NEWS_FEED = 'news_feed'
    UPDATE_STATUS = 'update_status'

class SystemMessages:
    EMPTY_UUID = 'uuid값이 없습니다'
    EMPTY_NAME = 'name값이 없습니다'
    REQUIRED_LOGIN_FIRST = '로그인을 먼저 해주세요'
    ALREADY_USER_EXISTED = '이미 존재하는 유저입니다'
    DATABASE_OPERATION_ERROR = '데이터베이스 에러'