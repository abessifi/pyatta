from sqlalchemy.schema import MetaData, DropConstraint
import pytest
from api.base_setup import app, db

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

