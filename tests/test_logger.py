#Imports
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from VyosSessionConfig import utils


def setup_module(module):
    """
    """
    pass

def teardow_module(module):
    """
    """
    pass

def test_filehandle():
    """
    Check if log file exists. Create it if not.
    """
    assert utils.get_log_filehandler() is not False

def test_init_logger():
    """
    Assert that multiple calls of init_logger() return the same logger object.
    """
    logger1 = utils.init_logger()
    logger2 = utils.init_logger()
    assert logger1 == logger2

def test_loglevel():
    """
    Test log level severity
    """
    assert utils.get_log_level() in ['DEBUG','INFO','WARN','ERROR','CRITICAL']
