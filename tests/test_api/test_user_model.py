import pytest
from api.base_setup import  db, User, UserAttributeNotValide

def test_user_model_validation():
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

def test_user_password():
    """
    Check if the user pass is correctely hashed
    """
    user = User(username='foobar', password='foo.bar', email='foo@bar.baz', superuser='0')
    password = 'foo.bar'
    assert user.verify_password(password) # assert that the pass hash is correct (authentication)
    
def test_user_password_changed():
    """
    Check if the user pass is correctly changed
    """
    user = User(username='foobar', password='foo.bar', email='foo@bar.baz', superuser='0')
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username='foobar')[0]
    old_pass = user.password
    user.password = 'blablabla'
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username='foobar')[0]
    assert old_pass != user.password

def test_user_set_email():
    """
    Test User mail setter
    """
    user = User(username='foobar', password='foo.bar', email='foo@bar.baz', superuser='0')
    user.email = 'foobar@foo.bar'
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username='foobar').all()[0]
    assert user.email == 'foobar@foo.bar'

def test_token_generation():
    """
    Test if temporaty token is correctely generated
    """
    user = User()
    assert user.generate_auth_token()

def test_verify_auth_token():
    """
    Assert token is valid/not valid
    """
    assert not User.verify_auth_token('this_is_not_a_valid_token')
    user = User(username='foo.bar', password='foobar', email='foo@bar.baz', superuser='0')
    db.session.add(user)
    db.session.commit()
    token = user.generate_auth_token()
    assert user.verify_auth_token(token)
