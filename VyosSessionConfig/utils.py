import ConfigParser
import subprocess
import os

# In production environment PROJECT_PATH should be /etc/pyatta/
PROJECT_PATH = "/home/vyos/vyos-api/project"
CONFIG_FILE_NAME = "pyatta.conf"

def _run(cmd, output=False):
    """
    To run command easier
    """
    if output:
        try:
            out = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            out = False
        return out
    try:
        out = subprocess.check_call(cmd, shell=True) # returns 0 for True
    except subprocess.CalledProcessError:
        out = 1 # returns 1 for False
    return out

def get_config_params(section, key):
    """
    To get specific parameters valuers from config file 
    """
    config = ConfigParser.SafeConfigParser()
    config.readfp(open(os.path.join(PROJECT_PATH, CONFIG_FILE_NAME)))
    return config.get(section, key)

def clean_environ(env):
    """
    Delete some envionment variables from system.
    """
    for key in env.keys():
        if os.environ.get('key'): del os.environ[key]
