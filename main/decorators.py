# -*- coding: utf-8 -*-
"""
	main.decorators
	~~~~~~~~~~~~~~~~~~~~
"""

from functools import wraps
from flask import session, request, g

from main.exceptions import APIException
from main.users.models import User

def login_required(f):
	"""로그인 decorator
	"""
	@wraps(f)
	def wrap(*args, **kwargs):
		if not 'user_id' in session:
			return '', 401
		if g.user is None:
			return '', 401
		return f(*args, **kwargs)
	return wrap
