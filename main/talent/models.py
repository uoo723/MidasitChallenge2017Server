# -*- coding: utf-8 -*-
"""
    main.talent.models
    ~~~~~~~~~~~~~~~~~~
"""

from datetime import datetime, timezone

from main import db

class Talent(db.Model):

    __tablename__ = 'talent'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
        db.ForeignKey('user.id', ondelete='cascade'), nullable=False) # 재능 기부 요청자
    title = db.Column(db.String(255), nullable=False)
    contents = db.Column(db.String(255), nullable=False)
    point = db.Column(db.Integer, default=100, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)  # 재능 요청 신청 완료 여부
    req_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    apply_talent = db.relationship('ApplyTalent', uselist=False, back_populates='talent')

    def get_data(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'contents': self.contents,
            'completed': self.completed,
            'req_at': int(self.req_at.timestamp()),
            'start_at': int(self.start_at.timestamp()),
            'end_at': int(self.end_at.timestamp())
        }

class ApplyTalent(db.Model):

    __tablename__ = 'apply_talent'

    id = db.Column(db.Integer, primary_key=True)
    talent_id = db.Column(db.Integer,
        db.ForeignKey('talent.id', ondelete='cascade'), nullable=False)
    contributor_id = db.Column(db.Integer,
        db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    talent = db.relationship('Talent', back_populates='apply_talent')

    def get_data(self):
        completed_at = int(self.completed_at.timestamp()) if self.completed_at else None
        return {
            'id': self.id,
            'talent_id': self.talent_id,
            'contributor_id': self.contributor_id,
            'completed_at': completed_at
        }

class DonationPlace(db.Model):

    __tablename__ = 'donation_place'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    contents = db.Column(db.String(255), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    target_point = db.Column(db.Integer, default=200, nullable=False)
    owned_point = db.Column(db.Integer, default=0, nullable=False)
    picture = db.Column(db.String(255), nullable=True)
    user_places = db.relationship('UserPlace', backref='donation_place')

    def get_data(self):
        return {
            'id': self.id,
            'title': self.title,
            'contents': self.contents,
            'due_date': int(self.due_date.timestamp()),
            'target_point': self.target_point,
            'owned_point': self.owned_point,
            'picture': self.picture
        }
