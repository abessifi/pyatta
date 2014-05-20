from api.base_setup import app, db
import api.pyatta
from flask.ext.webtest import TestApp

def setup_module():
    """
    Wrap flask application into TestApp
    """
    global application
    application = TestApp(app, db=db, use_session_scopes=True)

def test_ping_flask():
    """
    Check whether the application is responding correctly
    """
    resp = application.get('/', expect_errors=True)
    assert resp.status_int == 404
    assert resp.json.get('error') == 'Resource not found'

def test_unauthorized_access():
    """
    Test authorization. Server must return 403.
    """
    resp = application.get('/v1.0/token', expect_errors=True)
    assert resp.status_int == 403
    assert resp.json.get('error') == 'Unauthorized access !'

def authentication():
    """
    Test login action.
    """
    resp = application.post_json('/v1.0/auth', dict(username='itsme', password='changeme'), expect_errors=True)
    assert resp.status_int == 400
    assert resp.json.get('status') == 'error'

def is_admin():
    """
    Check if logged user is admin
    """
    resp = application.post_json('/v1.0/auth', dict(username='admin', password='notsecure'))
    assert resp.status_int == 200
    assert resp.session['su'] == True

def get_users():
    """
    """
    pass

def get_user():
    """
    """
    pass

def post_user():
    """
    """
    pass

def delete_user():
    """
    """
    pass

def update_user():
    """
    """
    pass

def valid_token():
    """
    """
    pass
