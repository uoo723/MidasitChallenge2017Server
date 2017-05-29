# -*- coding: utf-8 -*-
"""
    main.users.models
    ~~~~~~~~~~~~~~~~~

    유저 정보 DB 모델
"""

from main import db
from datetime import datetime, timezone

user_role = db.Table('user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='cascade'), 
        nullable=False),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete='cascade'),
        nullable=False))

class Role(db.Model):

    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    point = db.Column(db.Integer, nullable=False, default=0)
    profile = db.Column(db.String(255), nullable=True)
    push_token = db.Column(db.String(255), nullable=True)
    roles = db.relationship('Role', secondary=user_role,
        backref='users', lazy='dynamic')
    user_places = db.relationship('UserPlace', backref='user')
    point_histories = db.relationship('PointHistory', backref='user')

    def get_data(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'point': self.point,
        }

class UserPlace(db.Model):

    __tablename__ = 'user_place'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
        db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    place_id = db.Column(db.Integer,
        db.ForeignKey('donation_place.id', ondelete='cascade'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    point = db.Column(db.Integer, nullable=False)

class PointHistory(db.Model):

    __talbename__ = 'point_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
        db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    point = db.Column(db.Integer, nullable=False)

    def get_data(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': int(self.date.timestamp()),
            'point': self.point
        }