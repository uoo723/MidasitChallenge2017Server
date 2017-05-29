# -*- config: utf-8 -*-
"""
    main.talent.views
    ~~~~~~~~~~~~~~~~~
"""
import os, requests

from flask import Blueprint, request, session, g, jsonify, \
current_app

from datetime import datetime, timedelta, timezone

from main import db
from main.users.models import User, PointHistory, UserPlace
from main.talent.models import Talent, ApplyTalent, DonationPlace
from main.decorators import login_required

talent = Blueprint('talent', __name__)

@talent.route('/test', methods=['GET'])
def test():
    return '', 201

@talent.route('/my_requests', methods=['GET'])
@login_required
def my_requests():
    """나의 재능기부 요청 리스트 리턴

    :status 200: 요청완료
    :status 401: 로그인 필요
    :status 500: 서버 오류

    **성공 response**:
    
    .. sourcecode:: http

        HTTP/1.1 200 OK

        Content-Type: application/json

        [
            {
                "id": id,
                "user_id": user_id,             # 재능 기부 요청자 id (uuid 아님)
                "title": title,
                "contents": contents,
                "completed": completed,         # 재능 기부 신청 완료 여부 (기여자가)
                "completed_at": completed_at,   # 재능 기부가 완료되었는지 (수혜자가)
                "req_at": req_at,               # 등록일자 (unix time)
                "start_at": start_at,
                "end_at": end_at
            },
            ...
        ]

    **실패 response**:
    
    .. sourcecode:: http

        HTTP/1.1 401 Unauthorized
    """
    talents = Talent.query.filter_by(user_id=g.user.id)
    results = []

    for talent in talents:
        apply_talent = talent.apply_talent
        completed_at = None
        if apply_talent is not None:
            completed_at = apply_talent.completed_at
        result = talent.get_data()
        result['completed_at'] = completed_at
        results.append(result)

    results.sort(key=lambda k: k['req_at'], reverse=True)
    results.sort(key=lambda k: k['completed'], reverse=True)

    return jsonify(results)

@talent.route('/req_donation', methods=['POST'])
@login_required
def req_donataion():
    """재능 기부 요청 (재능 기부 수혜자)

    :form title: 제목
    :type title: str
    :form contents: 내용
    :type contents: str
    :form start_at: 시작일자 (unix time)
    :type start_at: int
    :form end_at: 종료일자 (unix time)
    :type end_at: int
    :status 201: 요청 완료
    :status 401: 로그인 필요
    :status 400: 폼데이터 오류
    :status 500: 서버 오류

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 201 CREATED

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 400 BAD REQUEST
    """
    title = request.form.get('title', type=str)
    contents = request.form.get('contents', type=str)
    start_at = request.form.get('start_at', type=int)
    end_at = request.form.get('end_at', type=int)

    if title is None:
        print('title')
        print(title)
        return '', 400

    if contents is None:
        print('contents')
        print(contents)
        return '', 400

    if start_at is None:
        print('start_at')
        print(start_at)
        return '', 400

    if end_at is None:
        print('end_at')
        print(end_at)
        return '', 400

    if end_at - start_at <= 0:
        print(end_at)
        print(start_at)
        print('end_at - start_at')
        print(end_at - start_at)
        return '', 400

    try:
        talent = Talent(
            user_id=g.user.id, 
            title=title, 
            contents=contents,
            start_at=datetime.fromtimestamp(start_at), 
            end_at=datetime.fromtimestamp(end_at))
        db.session.add(talent)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return '', 500

    return '', 201

@talent.route('/apply_donation', methods=['POST'])
@login_required
def apply_donation():
    """재능 기부 신청 (재능 기부 기여자)

    :form talent_id: talent id
    :type talent_id: int
    :status 201: 요청 완료
    :status 400: 폼 데이터 오류
    :status 401: 로그인 필요
    :status 404: talent not found
    :status 500: 서버 오류

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 201 CREATED

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 404 NOT FOUND
    """
    talent_id = request.form.get('talent_id', type=int)

    if talent_id is None:
        return '', 400

    talent = Talent.query.filter_by(id=talent_id)

    if talent.first() is None:
        return '', 404

    try:
        apply_talent = ApplyTalent(
            talent_id=talent_id,
            contributor_id=g.user.id)

        talent.update({'completed': True})
        db.session.add(apply_talent)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return '', 500

    return '', 201


@talent.route('/list', methods=['GET'])
@login_required
def talent_list():
    """재능 기부 신청 리스트 리턴

    :status 200: 요청 성공
    :status 401: 로그인 필요

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK

        Content-Type: application/json

        [
            {
                "id": id,
                "user_id": user_id,         # 재능 기부 요청자 id (uuid 아님)
                "title": title,
                "name": name,
                "contents": contents,
                "completed": completed,     # 재능 기부 신청 완료 여부
                "req_at": req_at,           # 등록일자 (unix time)
                "start_at": start_at,
                "end_at": end_at
            },
            ...
        ]

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 401 Unauthorized
    """
    today = datetime.utcnow()
    results = []

    talents = Talent.query.filter(
        Talent.completed == False)

    for talent in talents:
        t = talent.get_data()
        user = User.query.filter_by(id=t['user_id']).first()
        user_name = user.get_data()['name']
        t['name'] = user_name
        results.append(t)

    results.sort(key=lambda k: k['req_at'], reverse=True)

    return jsonify(results)

@talent.route('/<int:talent_id>', methods=['PUT'])
@login_required
def completed_donation(talent_id):
    """재능 기부 완료 (재능 수혜자가 완료요청)

    :status 200: 요청 완료
    :status 401: 로그인 필요
    :status 404: talent_id is not valid
    :status 409: 기여자 수혜자 동일
    :status 500: 서버 오류

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 401 Unauthorized
    """
    apply_talent = ApplyTalent.query.filter_by(talent_id=talent_id)
    talent = Talent.query.filter_by(id=talent_id).first()
    user = User.query.filter_by(id=g.user.id)

    if apply_talent.first() is None:
        return '', 404

    contributor_id = apply_talent.first().contributor_id

    if g.user.id == contributor_id:
        return '', 409

    try:
        apply_talent.update({'completed_at': datetime.utcnow()})
        user_point = user.first().point
        user_point += talent.point
        user.update({'point': user_point})

        point_history = PointHistory(user_id=contributor_id, point=user_point)

        db.session.add(point_history)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return '', 500
    return '', 200

@talent.route('/completed', methods=['GET'])
@login_required
def completed():
    """봉사활동 완료 내역 리스트 리턴

    :status 200: 요청 완료
    :status 401: 로그인 필요
    :status 500: 서버 오류

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK

        [
            {
                "id": id,
                "talent_id": talent_id,
                "title": title,
                "contents": contents,
                "contributor_id": contributor_id,
                "completed_at": completed_at        # unix time
            },
            ...
        ]

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 401 Unauthorized
    """
    apply_talents = ApplyTalent.query.filter(
        ApplyTalent.contributor_id == g.user.id,
        ApplyTalent.completed_at != None)

    results = []

    for apply_talent in apply_talents:
        talent = apply_talent.talent.get_data()
        result = apply_talent.get_data()
        result['title'] = talent['title']
        result['contents'] = talent['contents']
        results.append(result)

    results.sort(key=lambda k: k['completed_at'], reverse=True)

    return jsonify(results)

@talent.route('/donation_list', methods=['GET'])
def donation_list():
    """포인트 기부 사용처 리스트

    :status 200: 요청 완료
    :status 500: 서버 오류

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK

        [
            {
                "id": id,
                "title": title,
                "contents": contents,
                "due_date": due_date,            # unix time
                "target_point": target_point,    # 목표 기부포인트
                "owned_point": owned_point,      # 현재 기부포인트
            },
            ...
        ]

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 500 Internal Server Error
    """
    today = datetime.utcnow()
    places = DonationPlace.query.filter(DonationPlace.due_date >= today)
    results = []

    for place in places:
        p = place.get_data()
        if p['target_point'] > p['owned_point']:
            results.append(p)

    return jsonify(results)

@talent.route('/donate_point', methods=['PUT'])
@login_required
def donate_point():
    """포인트 기부

    :form place_id: 사용처 아이디
    :type place_id: int
    :form point: 기부할 포인트
    :type point: int
    :status 200: 업데이트 성공
    :status 400: 폼 데이터 오류
    :status 401: 로그인 필요
    :status 404: place_id가 유효하지 않음
    :status 422: point가 자신이 가지고 있는 것보다 많을 때
    :status 500: 서버 오류

    **성공 response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK

    **에러 response**:

    .. sourcecode:: http

        HTTP/1.1 500 Internal Server Error
    """
    place_id = request.form.get('place_id', type=int)
    point = request.form.get('point', type=int)

    if place_id is None:
        return '', 400

    if point is None:
        return '', 400

    user = User.query.filter_by(id=g.user.id)
    place = DonationPlace.query.filter_by(id=place_id)

    if place.first() is None:
        return '', 404

    if point > user.first().point:
        return '', 422

    user_point = user.first().point - point
    place_point = place.first().owned_point + point

    try:
        user.update({'point': user_point})
        place.update({'owned_point': place_point})

        user_id = user.first().id
        place_id = place.first().id

        user_place = UserPlace.query.filter_by(user_id=user_id, place_id=place_id)
        if user_place.first() is None:
            user_place = UserPlace(user_id=user_id, place_id=place_id, point=point)
            db.session.add(user_place)
        else:
            user_place_point = user_place.first().point + point
            user_place.update({'point': user_place_point, 'date': datetime.utcnow()})

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return '', 500
    return '', 200

