from sqlalchemy.schema import MetaData, DropConstraint
import pytest

import api.base_setup as bs
from api.base_setup import app, db, User


#def setup_module(module):
    #"""
    #Initialize the db and app for tests
    #"""
    # NOTE : we could use app.test_client() as a web client to test interraction with flask.
    # app.config['TESTING'] = True # in order for the exceptions to propagate to a test client.
    # Indeed we opte to WebTest framework regarding its advanced testing features.
    #db.create_all()

#def teardown_module(module):
    #"""
    #Reset database contents
    #"""
    #db.session.remove()
    #db.drop_all()

@pytest.fixture(scope='session')
def application(request):
    return app

@pytest.fixture(scope='session', autouse=True)
def setup_db(request, application):
    # Clear out any existing tables
    metadata = MetaData(db.engine)
    metadata.reflect()
    for table in metadata.tables.values():
        for fk in table.foreign_keys:
            db.engine.execute(DropConstraint(fk.constraint))
    metadata.drop_all()

    # Create the tables based on the current model
    db.create_all()
    # Add base data here
    # ...
    db.session.flush()
    db.session.expunge_all()
    db.session.commit()

@pytest.fixture(autouse=True)
def dbsession(request, monkeypatch):
    # Roll back at the end of every test
    request.addfinalizer(db.session.remove)
    # Prevent the session from closing (make it a no-op) and
    # committing (redirect to flush() instead)
    monkeypatch.setattr(db.session, 'commit', db.session.flush)
    monkeypatch.setattr(db.session, 'remove', lambda: None)

def test_db_config():
    """
    Check user db config
    """
    assert bs.check_db_config()

def test_db_create_user():
    """
    Test user creation 
    """
    User.query.delete()
    assert len(User.query.all()) == 0
    user = User(username='foo', password='bar', email='foo@bar', superuser='0')
    db.session.add(user)
    db.session.commit()
    assert len(User.query.all()) == 1

