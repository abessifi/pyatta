import pytest
from api.base_setup import app, db, User, check_db_config, UserAttributeNotValide

def setup_module(module):
    """
    Check user db config
    """
    check_db_config()

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
    with pytest.raises(UserAttributeNotValide) as e:
        user = User(username='foo', password='foo.bar', email='foo.bar', superuser='0')
        db.session.add(user)
        db.session.commit()
    assert e.value.message == 'username not valide'
    # test email validation
    with pytest.raises(UserAttributeNotValide) as e:
        user = User(username='foo.bar', password='foo.bar', email='foo.bar', superuser='0')
        db.session.add(user)
        db.session.commit()
    assert e.value.message == 'email not valide' or e.value.message == 'password not valide'
    # assert user creation
    user = User(username='foo.bar', password='foobar', email='foo@bar.baz', superuser='0')
    db.session.add(user)
    db.session.commit()
    assert len(User.query.all()) == 1
