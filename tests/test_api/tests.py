from main import app, db
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
    resp = application.get('/')
    assert resp.status_int == 200

def test_authentication_success():
    """
    Test login action. Authentication must succeed.
    """
    resp = application.post_json('/v1.0/auth', dict(username='itsme', password='changeme'))
    assert resp.status_int == 200
    assert resp.json.get('status') == 'success'
    assert len(resp.json.get('auth')['token']) > 0

def test_authentication_failed():
    """
    Test login action. Authentication must fail.
    """
    resp = application.post_json('/v1.0/auth', dict(username='', password=''), expect_errors=True)
    assert resp.status_int == 400
    assert resp.json.get('status') == 'error'

def test_is_admin():
    """
    Check if logged user is admin
    """
    resp = application.post_json('/v1.0/auth', dict(username='admin', password='notsecure'))
    assert resp.status_int == 200
    assert resp.session['su'] == True

def test_get_users():
    """
    """
    pass

def test_get_user():
    """
    """
    pass

def test_post_user():
    """
    """
    pass

def test_delete_user():
    """
    """
    pass

def test_update_user():
    """
    """
    pass

def test_valid_token():
    """
    """
    pass
