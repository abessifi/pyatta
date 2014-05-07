import api_setup
import pytest

import api.base_setup as bs
from api.base_setup import app, db, User


#Initialize the db and app for tests
# NOTE : we could use app.test_client() as a web client to test interraction with flask.
# app.config['TESTING'] = True # in order for the exceptions to propagate to a test client.
# Indeed we opte to WebTest framework regarding its advanced testing features.


def test_db_config():
    """
    Check user db config
    """
    assert bs.check_db_config()

def test_user_password():
    """
    Check if the user pass is correctely hashed
    """
    user = User(username='foobar', password='foo.bar', email='foo@bar.baz', superuser='0')
    password = 'foo.bar'
    user.hash_password(password)
    assert user.password != password # assert that the pass is hashed
    assert user.verify_password(password) # assert that the pass hash is correct (authentication)


def test_user_model():
    """
    Test user creation 
    """
    User.query.delete()
    assert len(User.query.all()) == 0
    
    # test usename validation
    with pytest.raises(bs.UserAttributeNotValide) as e:
        user = User(username='foo', password='foo.bar', email='foo.bar', superuser='0')
        db.session.add(user)
        db.session.commit()
    assert e.value.message == 'username not valide'
    # test email validation
    with pytest.raises(bs.UserAttributeNotValide) as e:
        user = User(username='foo.bar', password='foo.bar', email='foo.bar', superuser='0')
        db.session.add(user)
        db.session.commit()
    assert e.value.message == 'email not valide' or e.value.message == 'password not valide'
    # assert user creation
    user = User(username='foo.bar', password='foobar', email='foo@bar.baz', superuser='0')
    db.session.add(user)
    db.session.commit()
    assert len(User.query.all()) == 1
