import pytest
from execformat.executor import session, check_operation_name, execUtils, OperationNameError, OperationFailed
from vyos_session.configsession import SessionNotExists

def setup_module(module):
    """
    Set up a config session
    """
    session.setup_config_session()

def teardown_module(module):
    """
    Teardown created config session
    """
    session.teardown_config_session()

def test_check_operation_name():
    """
    Test if operation/command name is correct.
    """
    args = []
    with pytest.raises(OperationNameError) as e:
        check_operation_name(args)
    assert e.value.message == 'Operation name required.'

    args = ['true']
    with pytest.raises(OperationNameError) as e:
        check_operation_name(args)
    assert e.value.message == 'Operation name not correct.'

    args = ['set']
    assert check_operation_name(args) == True

def test_execmd_out_of_session():
    """
    Assert that config commands are not performed if vyos session is not set up
    """
    #teardown session because it is yet set up by setup_module()
    args = ['show','nat','source']
    session.teardown_config_session()
    #execmd would fail. Otherwise, there is a bug :p
    with pytest.raises(SessionNotExists) as e:
        execUtils().execmd(args)
    assert e.value.message == 'Configure session do not exists'
    #resetup session to continue executing remaining tests 
    session.setup_config_session()

def test_execmd_missed_args():
    """
    Assert that 'set' command fails because of incomplet args.
    """
    args = ['set']
    with pytest.raises(OperationFailed) as e:
        execUtils().execmd(args)
    assert e.value.message == 'Operation failed !'

def test_execmd_show():
    """
    Test if show command is correctely executed.
    """
    args = ['show','nat','source']
    success, out = execUtils().execmd(args)
    assert success == True

def test_set_iface_desc():
    """
    Test if the description of a giving interface is correctly set.
    """
    args = ['set','interfaces','ethernet','eth3','description','"This is a LAN interface"']
    success, out = execUtils().execmd(args)
    assert success == True
    session.commit()
    args = ['show','interfaces','ethernet','eth3','description']
    success, out = execUtils().execmd(args)
    assert out.split('"')[1] == "This is a LAN interface"
