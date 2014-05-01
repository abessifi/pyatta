import ConfigParser
import subprocess
import os
import logging

# In production environment CONFIG_DIR should be /etc/pyatta/
CONFIG_DIR = "/home/vyos/vyos-api/project"
CONFIG_FILE_NAME = "pyatta.conf"
AVAILABLE_LOG_LEVELS = ['DEBUG','INFO','WARN','ERROR','CRITICAL']
DEFAULT_LOG_LEVEL = 'INFO'

logger = logging.getLogger(__name__)

def get_config_params(section, key):
    """
    To get specific parameters valuers from config file 
    """
    config = ConfigParser.SafeConfigParser()
    config.readfp(open(os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)))
    return config.get(section, key)

def get_log_level():
    """
    Get and check log level value from pyatta.conf file.
    """
    log_level = get_config_params('log', 'level')
    if log_level not in AVAILABLE_LOG_LEVELS:
        print('[ERROR] Unknown log level !')
        return DEFAULT_LOG_LEVEL
    return log_level

def get_log_filehandler():
    """
    Create file handler which logs messages.
    """
    log_dir = get_config_params('log', 'logdir')
    log_file = get_config_params('log', 'logfile')
    log_file_path = os.path.join(log_dir, log_file)
    
    if not os.path.exists(log_dir) or not os.path.exists(log_file_path):
        try:
            os.makedirs(log_dir)
            open(log_file_path, 'a').close()
        except OSError as exception:
            print exception
            return False
        print "[INFO] Create log file %s" % log_file_path
    # create file handler
    fh = logging.FileHandler(log_file_path,'a')
    fh.setLevel(eval('logging.{}'.format(get_log_level())))
    return fh

def init_logger(logger):
    """
    Initialize logger object for logging application's activities to a specific file.
    """
    # create logger
    logger.setLevel(eval('logging.{}'.format(get_log_level())))
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = get_log_filehandler()
    file_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(file_handler)

def _run(cmd, output=False):
    """
    To run command easier
    """
    if output:
        try:
            logger.debug('exec command: "%s"', cmd)
            out = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            return False
        logger.debug('command output: %s', out)
        return ' '.join(out.splitlines())
    try:
        logger.debug('exec command: "%s"', cmd)
        out = subprocess.check_call(cmd, shell=True) # returns 0 for True
    except subprocess.CalledProcessError:
        out = 1 # returns 1 for False
    logger.debug('command return code: %s', out)
    return out

def clean_environ(env):
    """
    Delete some envionment variables from system.
    """
    for key in env.keys():
        if os.environ.get('key'): del os.environ[key]

#initilize the logger for this module
init_logger(logger)
