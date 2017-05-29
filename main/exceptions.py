# -*- coding: utf-8 -*-
"""
    main.exceptions
    ~~~~~~~~~~~~~~~~~~~~
"""

class APIException(Exception):
    """APIException object

        :param message: 에러 메세지
        :type message: str
        :param code: 에러 코드 -> main.constants.ErrorCode
        :type code: int
        :param status_code: HTTP 상태 코드
        :type status_code: int
        :param payload: 추가 정보
        :type payload: dict
    """
    status_code = 400

    def __init__(self, message, code='API_ERROR', status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.code = code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['code'] = self.code
        return rv