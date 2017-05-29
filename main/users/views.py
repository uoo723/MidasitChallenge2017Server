# -*- coding: utf-8 -*-
"""
    main.users.views
    ~~~~~~~~~~~~~~~~

    유저 관련 HTTP 요청 처리 모듈
 """
import os, requests

from io import StringIO
from PIL import Image

from flask import Blueprint, request, session, g, jsonify, \
current_app, send_file

from datetime import datetime

from main import db, fcm
from main.users.models import User, Role
from main.exceptions import APIException
from main.decorators import login_required
from main.helpers import allowed_file, secure_filename

users = Blueprint('users', __name__)

@users.route('/test', methods=['POST'])
def test():
    return '', 201

@users.route('/test_list', methods=['GET'])
def testList():
    users = User.query.all()
    results = []

    for user in users:
        results.append(user.get_data())

    return jsonify(message='Succeed to get list', results=results)

@users.route('/sign_up', methods=['POST'])
def signUp():
    """회원 가입

    :form uuid: 디바이스 uuid
    :type uuid: str
    :form name: 이름
    :type name: str
    :status 201: 요청 완료
    :status 400: 잘못된 데이터
    :status 409: 이미 존재하는 유저
    :status 500: 서버 오류
    
    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 201 CREATED

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 400 BAD REQUEST
    """
    uuid = request.form.get('uuid', type=str)
    name = request.form.get('name', type=str)

    if uuid is None:
        return '', 400

    if name is None:
        return '', 400

    user = User.query.filter_by(uuid=uuid).first()

    if user is not None:
        session['user_id'] = user.id
        return '', 201

    try:
        role = Role.query.filter_by(name='user')
        user = User(name=name, uuid=uuid, roles=role)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return '', 500

    session['user_id'] = user.id

    return '', 201

@users.route('/login', methods=['POST'])
def login():
    """로그인

    :form uuid: 디바이스 uuid
    :type uuid: str
    :form name: 유저 이름
    :type name: str
    :status 200: 요청 완료
    :status 400: 잘못된 데이터
    :status 404: 존재하지 않는 유저
    :status 500: 서버 오류

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK

        Content-Type: application/json

        {
            "id": id,
            "uuid": uuid,
            'name': name,
            "point": point
        }

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 400 BAD REQUEST
    """
    uuid = request.form.get('uuid', type=str)
    name = request.form.get('name', type=str)

    if uuid is None:
        return '', 400

    if name is None:
        return '', 400

    user = User.query.filter_by(uuid=uuid).first()

    if user is None:
        return '', 404

    # if user.name != name:
    #     return '', 404

    session['user_id'] = user.id

    return jsonify(user.get_data())

@users.route('/me', methods=['GET'])
@login_required
def me():
    """본인 정보 리턴

    :status 200: 요청 완료
    :status 401: 로그인 필요
    :status 500: 서버 오류

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK

        Content-Type: application/json

        {
            "id": id,
            "uuid": uuid,
            'name': name,
            "point": point
        }

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 401 Unauthorized
    """
    return jsonify(g.user.get_data())

@users.route('/profile', methods=['POST'])
@login_required
def profile():
    """프로필 사진 등록

    :form profile: 프로필 ('png', 'jpg', 'jpeg', 'gif')
    :type profile: raw (bytes)
    :status 201: 요청 완료
    :status 401: 로그인 필요
    :status 400: 폼데이터 오류(요청 파일의 확장자가 다를 때도 포함)
    :status 500: 서버 오류

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 201 CREATED

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 400 BAD REQUEST
    """
    profile = request.files.get('profile')

    if profile is None:
        print('profile is None')
        return '', 400

    if not allowed_file(profile.filename):
        print(profile.filename)
        return '', 400

    filename = secure_filename(profile.filename)
    profile_path = os.path.join(current_app.config['UPLOAD_DIR'], filename)

    user = User.query.filter_by(id=g.user.id)

    old_profile_path = user.first().profile
    if old_profile_path and os.path.isfile(old_profile_path):
        os.remove(old_profile_path)                 # 기존 프로필 삭제

    try:
        user.update({'profile': profile_path})
        db.session.commit()
        profile.save(profile_path)
    except:
        db.session.rollback()
        return '', 500

    return '', 201

@users.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """유저 프로필 리턴

    :status 200: 요청 완료
    :status 404: 프로필 찾을 수 없음

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK

        binary data

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
    """
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return '', 404

    if user.profile is None:
        return '', 404

    return send_file(user.profile)

@users.route('/user/<uuid>', methods=['DELETE'])
def delete_user(uuid):
    """유저 삭제

    :status 200: 삭제 완료
    :status 404: 찾을 수 없음
    :status 500: 서버 오류

    **성공 response**:
    
    .. sourcecode:: http

        HTTP/1.1 200 OK

    **실패 response**:
    
    .. sourcecode:: http

        HTTP/1.1 404 Not Found
    """
    user = User.query.filter_by(uuid=uuid)

    if user.first() is None:
        return '', 404

    apply_talent = ApplyTalent.query().filter_by(contributor_id=user.first().id)
    talent = apply_talent.talent

    try:
        user.delete()
        talent.update({'completed': False})
        db.session.commit()
    except:
        db.session.rollback()
        return '', 500
    return '', 200

@users.route('/donations', methods=['GET'])
@login_required
def donations():
    """포인트 기부 내역 리스트 리턴

    :status 200: 요청 완료
    :status 401: 로그인 필요
    :status 500: 서버 오류

    **성공 response**:
    
    .. sourcecode:: http

        HTTP/1.1 200 OK

        [
            {
                "id": id,
                "title": title,
                "contents": contents,
                "due_date": due_date,            # 만기 날짜 unix time
                "target_point": target_point,    # 목표 기부포인트
                "owned_point": owned_point,      # 현재 기부포인트
                "contri_point": contri_point,    # 내 기여 포인트
                "date": date                     # 최근 기여 날짜 unix time
            },
            ...
        ]

    **실패 response**:
    
    .. sourcecode:: http

        HTTP/1.1 401 Unauthorized
    """
    user = User.query.filter_by(id=g.user.id).first()
    results = []

    for user_place in user.user_places:
        donation_place = user_place.donation_place
        result = donation_place.get_data()
        result['contri_point'] = user_place.point
        result['date'] = user_place.date
        results.append(result)

    return jsonify(results)

@users.route('/point_history', methods=['GET'])
@login_required
def point_history():
    """본인의 포인트 히스토리 리턴

    :status 200: 요청 완료
    :status 500: 서버 오류

    **성공 response**:
    
    .. sourcecode:: http

        HTTP/1.1 200 OK

        [
            {
                "id": id,
                "user_id": user_id,
                "date": date,
                "point": point
            },
            ...
        ]

    **실패 response**:
    
    .. sourcecode:: http

        HTTP/1.1 500 Internal Server Error
    """
    user = User.query.filter_by(id=g.user.id).first()
    point_histories = user.point_histories
    results = []

    for history in point_histories:
        results.append(history.get_data())

    results.sort(key=lambda k: k['date'])

    return jsonify(results)

@users.route('/token', methods=['PUT'])
@login_required
def token():
    """토큰 등록

    :status 200: 요청완료
    :status 400: 폼데이터 오류
    :status 401: 로그인 필요
    :status 500: 서버 오류

    **성공 response**:
    
    .. sourcecode:: http

        HTTP/1.1 200 OK

    **실패 response**:
    
    .. sourcecode:: http

        HTTP/1.1 500 Internal Server Error
    """
    token = request.form.get('token', type=str)

    if token is None:
        return '', 400

    user = User.query().filter_by(id=g.user.id)

    try:
        user.update({'push_token': token})
        db.session.commit()
    except:
        db.session.rollback()
        return '', 500
    return '', 200

@users.route('/push_noti', methods=['POST'])
def push_noti():
    """푸쉬

    :form title: 제목
    :type title: str
    :form body: 내용
    :type body: str
    :form to: 수신 유저 아이디
    :type to: int
    :status 200: 요청완료
    :status 400: 폼데이터 오류
    :status 404: not found user or token 
    :status 408: 푸쉬 전송 실패
    :status 500: 서버 오류

    **성공 response**:
    
    .. sourcecode:: http

        HTTP/1.1 200 OK

    **실패 response**:
    
    .. sourcecode:: http

        HTTP/1.1 500 Internal Server Error
    """
    title = request.form.get('title', type=str)
    body = request.form.get('body', type=str)
    to = request.form.get('to', type=int)

    if title is None:
        return '', 400

    if body is None:
        return '', 400

    if to is None:
        return '', 400

    user = User.query.filter_by(id=to).first()

    if user is None:
        return '', 404

    token = user.push_token

    if token is None:
        return '', 404

    data = {
        'title': title,
        'body': body
    }

    try:
        fcm.notify_single_device(token, data)
    except Exception as e:
        print(e)
        return '', 408
    return '', 200