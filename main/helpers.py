# -*- coding: utf-8 -*-
"""
    main.helpers
    ~~~~~~~~~~~~~~~~~
"""
import random

from datetime import datetime

def allowed_file(filename):
    """업로드 파일 형식 제한

    :param filename: 확장자를 포함하는 파일 이름
    :type filename: str
    :returns: 허용 True, 제한 False
    :rtype: bool
    """
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

    return '.' in filename and \
    filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def secure_filename(filename, prefix='profile', length=8):
    """랜덤으로 고유한 파일 이름 생성

    유저가 올리는 파일 이름이 서버에 저장된 파일에 overwrite되지 않게

    :param filename: 확장자를 포함한 원래의 파일 이름
    :type filename: str
    :param prefix: 생성할 파일 이름의 접두어
    :type prefix: str
    :param length: 마지막 파일 이름의 랜덤 숫자 길이
    :type length: int
    :returns: 고유한 파일 이름, 형식 [prefix]_[업로드 날짜]_[랜덤 숫자].[확장자]
    :rtype: str
    """
    extension = filename.rsplit('.', 1)[1]
    suffix = ''.join(str(random.randint(0, 9)) for _ in range(length))
    return prefix + '_' + datetime.utcnow().strftime('%Y%m%d%H%M') + '_' + \
    suffix + '.' + extension