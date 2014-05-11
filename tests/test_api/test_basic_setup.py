import api.base_setup as bs


#Initialize the db and app for tests
# NOTE : we could use app.test_client() as a web client to test interraction with flask.
# app.config['TESTING'] = True # in order for the exceptions to propagate to a test client.
# Indeed we opte to WebTest framework regarding its advanced testing features.


def test_db_config():
    """
    Check user db config
    """
    assert bs.check_db_config()
