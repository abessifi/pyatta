import api.base_setup as bs

def test_db_exists():
    """
    Check user db config
    """
    assert bs.check_db_config()
