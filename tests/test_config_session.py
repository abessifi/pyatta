import pytest
import os
import uuid
from vyos_session.configsession import ConfigSession, SessionAlreadyExists
from vyos_session import utils
from execformat.executor import session

def setup_module(module):
    """
    Set up a config session
    """
    # do nothing
    #session.setup_config_session()
    pass

def teardown_module(module):
    """
    teardown created config session
    """
    session.teardown_config_session()

def test_config_parser():
    """
    Test if some config params are correctly set.
    """
    if os.path.isfile('/home/vyos/vyos-api/pyatta.conf'):
        assert utils.get_config_params('bin','shell_api_path') == '/bin/cli-shell-api'
        
def test_singleton_session():
    """
    Test if vsc.sessionconfig() is a singleton
    """
    with pytest.raises(SessionAlreadyExists) as e : 
        ConfigSession()
    assert e.value.message == 'A session exist already !'

def test_setup_session():
    """
    Test if vyos session is set up correctely. Check also if environment variables are exists.
    """
    assert session.setup_config_session() == True

    for env_var in session.session_envs.keys():
        assert session.session_envs.get(env_var) == os.environ.get(env_var)
    ## This test could be extended as follow in order to check if SetupSessionFailed
    ## exception is raised when attempting to create a vyos session (this is not mandatory).
    # do not forget to import SetupSessionFailed 
    #with pytest.raises(SetupSessionFailed) as e :
    #    session.setup_config_session()
    #assert e.value.message == 'Could not create session !'

def test_inSession():
    """
    Test if current session is available.
    """
    assert session.session_exists() == True

def test_session_changed():
    """
    Test if configuration was changed from current session
    """
    assert session.session_changed() == False

def test_discard_changes():
    """
    Test if discard action undo last config modifications.
    """
    assert session.discard() == 'No changes have been discarded'

def test_commit():
    """
    Test if changes are successfully commited
    """
    out = utils._run('/opt/vyatta/sbin/my_set interfaces ethernet eth3 description "This is a LAN interface"', output=True)
    #with pytest.raises(vsc.OperationFailed) as e:
    #    session.commit()
    assert session.commit() == True

def test_save_changes():
    """
    Test if changes are successfully saved in system.
    """
    assert session.save() == True
