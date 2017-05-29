# -*- coding: utf-8 -*-
"""
    main
    ~~~~
"""
import os

from flask import Flask, jsonify, g, session, \
send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_gcm import GCM
from flask_fcm import FCM
from main.constants import ErrorCode

db = SQLAlchemy()
gcm = GCM()
fcm = FCM()

def create_app(config='config.TestConfiguration'):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    gcm.init_app(app)
    fcm.init_app(app)

    # Define the default url prefix
    default_url_prefix = app.config['REST_API_VERSION_URL_PREFIX']

    from main.users.views import users
    from main.talent.views import talent

    # Register blueprint
    app.register_blueprint(users,
        url_prefix=default_url_prefix + '/users')
    app.register_blueprint(talent,
        url_prefix=default_url_prefix + '/talent')
    
    from main.exceptions import APIException

    @app.errorhandler(APIException)
    def handle_api_exception(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify(message='Not found', code=ErrorCode.NOT_FOUND), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify(message='Method Not Allowed', 
            code=ErrorCode.METHOD_NOT_ALLOWED), 405

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        return jsonify(message='Internal Server error',
            code=ErrorCode.INTERNAL_SERVER_ERROR), 500

    @app.errorhandler(408)
    def handle_request_timeout(error):
        return jsonify(message='Request Timeout',
            code=ErrorCode.REQUEST_TIMEOUT), 408

    from main.users.models import User
    from main.talent.models import Talent

    @app.before_request
    def load_user():
        g.user = \
        User.query.filter_by(id=session['user_id']).first() \
        if 'user_id' in session else None

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.close()
        # print("app teardown")
        # if exception is not None:
        #   print exception
    return app

app = create_app('config.DebugConfiguration')

@app.route('/api_docs')
def api_docs():
    return render_template('api_docs.html')

@app.route('/_static/<path:filename>')
def send_static_file(filename):
    base_dir = app.config['BASE_DIR']
    filename_path = os.path.join('docs/build/html/_static', filename)
    return send_file(os.path.join(base_dir, filename_path))
