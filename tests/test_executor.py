import pytest
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from execformat.executor import session, check_operation_name, execUtils, OperationNameError, OperationFailed, ConfigPathNotCorrect
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
        handler = execUtils(args)
        handler.execmd()
    assert e.value.message == 'Configure session do not exists'
    #resetup session to continue executing remaining tests 
    session.setup_config_session()

def test_execmd_missed_args():
    """
    Assert that 'set' command fails because of incomplet args.
    """
    args = ['set']
    with pytest.raises(OperationFailed) as e:
        handler = execUtils(args)
        handler.execmd()
    assert e.value.message == 'Operation failed !'

def test_execmd_show():
    """
    Test if show command is correctely executed.
    """
    args = ['show','nat','source']
    handler = execUtils(args)
    success, out = handler.execmd()
    assert success == True

def test_set_iface_desc():
    """
    Test if the description of a giving interface is correctly set.
    """
    args = ['set','interfaces','ethernet','eth2','description','"This is a LAN interface"']
    handler = execUtils(list(args))
    success, out = handler.execmd()
    assert success == True
    session.commit()
    args = ['show','interfaces','ethernet','eth2','description']
    handler = execUtils(list(args))
    success, out = handler.execmd()
    assert args[0] == 'show'
    assert out.split('"')[1] == "This is a LAN interface"

def test_check_cmd_args():
    """
    Test if config path is correctly checked
    """
    #Config path is correct
    args = ['show','interfaces','ethernet','eth2','description']
    handler = execUtils(list(args))
    assert handler.check_cmd_args() == True
    #Config path not correct
    args = ['show','foo', 'bar']
    with pytest.raises(ConfigPathNotCorrect) as e:
        handler = execUtils(list(args))
        handler.check_cmd_args()
    assert e.value.message == 'Configuration path is not correct'

def test_show_list_nodes():
    """
    Check if a list of nodes under specified configuration path is correctly returned
    """
    #Config path with more options
    args = ['show','interfaces','ethernet']
    handler = execUtils(list(args))
    success, options = handler.get_possible_options()
    assert success and len(options)
    #Config path without possible options
    args = ['show','interfaces','ethernet','eth2','description']
    handler = execUtils(list(args))
    success, options = handler.get_possible_options()
    assert success and not len(options)
    #Config path is not correct
    args = ['show','foo']
    handler = execUtils(list(args))
    success, options = handler.get_possible_options()
    assert not success and not len(options)
