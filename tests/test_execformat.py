import pytest
import sys

sys.path.append('/home/vyos/vyos-api/project')
from ExecFormat import execformat
from VyosSessionConfig import configsession as vsc
#from VyosSessionConfig import utils

sessionCfg = None

def setup_module(module):
    """
    Set up a config session
    """
    global sessionCfg
    sessionCfg = vsc.ConfigSession()
    sessionCfg.setup_config_session()

def teardown_module(module):
    """
    Teardown created config session
    """
    global sessionCfg
    sessionCfg.teardown_config_session()
    del sessionCfg

def test_check_operation_name():
    """
    Test if operation/command name is correct.
    """
    args = []
    with pytest.raises(execformat.OperationNameError) as e:
        execformat.check_operation_name(args)
    assert e.value.message == 'Operation name required.'

    args = ['true']
    with pytest.raises(execformat.OperationNameError) as e:
        execformat.check_operation_name(args)
    assert e.value.message == 'Operation name not correct.'

    args = ['set']
    assert execformat.check_operation_name(args) == True

def test_execmd_missed_args():
    """
    Assert that 'set' command fails because of incomplet args.
    """
    args = ['set']
    with pytest.raises(execformat.OperationFailed) as e:
        execformat.execUtils().execmd(args)
    assert e.value.message == 'Operation failed !'

def test_execmd_show():
    """
    Test if show command is correctely executed.
    """
    args = ['show','nat','source']
    success, out = execformat.execUtils().execmd(args)
    assert success == True

def test_set_iface_desc():
    """
    Test if the description of a giving interface is correctly set.
    """
    args = ['set','interfaces','ethernet','eth3','description','"This is a LAN interface"']
    success, out = execformat.execUtils().execmd(args)
    assert success == True
    sessionCfg.commit()
    args = ['show','interfaces','ethernet','eth3','description']
    success, out = execformat.execUtils().execmd(args)
    assert out.split('"')[1] == "This is a LAN interface"
