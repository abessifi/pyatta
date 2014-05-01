import os
from uuid import uuid4
from utils import get_config_params, _run, clean_environ, init_logger
import logging

logger = logging.getLogger(__name__)
init_logger(logger)

VYOS_SHELL_API = get_config_params('bin', 'shell_api_path')
VYOS_SBIN_DIR = get_config_params('bin', 'vyos_sbin_dir')
VYOS_SAVE_SCRIPT = 'vyatta-save-config.pl'

# Create/Get the logger object
#logger = init_logger()

class SessionAlreadyExists(Exception): pass
class SetupSessionFailed(Exception): pass
class OperationFailed(Exception): pass
class SessionNotExists(Exception): pass

class Session(object):
    """
    Return the session instance if exists. Else, create new one.
    SessionAlreadyExists exception raised on the second instantiation.
    """
    _ref = None
    def __new__(cls, *args, **kw):
        if cls._ref is not None:
            raise SessionAlreadyExists('A session exist already !')
        cls._ref = super(Session, cls).__new__(cls, *args, **kw)
        return cls._ref

class ConfigSession(Session):
    """
    Create and manage a Vyos config session.
    This is a singleton subclass of Session class which ensures that one and one config session only is opened.
    To create instance you have to call setup_config_session() method.
    """

    def setup_config_session(self):
        """
        Setup vyos session. A random uuid is generated as a sesssion identifier 
        ($PPID -Shell PID- could be used as well).
        """
        identifier = uuid4()
        env = {}
        env['VYATTA_CHANGES_ONLY_DIR'] = '/opt/vyatta/config/tmp/changes_only_{}'.format(identifier)
        env['VYATTA_CONFIG_TEMPLATE'] = '/opt/vyatta/share/vyatta-cfg/templates'
        env['VYATTA_ACTIVE_CONFIGURATION_DIR'] = '/opt/vyatta/config/active'
        env['VYATTA_EDIT_LEVEL'] = '/'
        env['VYATTA_TEMP_CONFIG_DIR'] = '/opt/vyatta/config/tmp/new_config_{}'.format(identifier)
        env['VYATTA_TEMPLATE_LEVEL'] = '/'
        env['VYATTA_CONFIG_TMP'] = '/opt/vyatta/config/tmp/tmp_{}'.format(identifier)
        # Add vyos session environment to system environment. This is not good but actually it seems
        # that is the only way to handle a persistant vyos session after spawning a shell.
        os.environ.update(env)
        logger.info('Setting up a configuration session for Vyos')
        # Spawn shell and setup vyos config session
        if _run('{} setupSession'.format(VYOS_SHELL_API)):
            # Unset vyos session environment and raise an exception
            logger.error('Could not create configuration session')
            logger.info('Cleaning up session environment variables')
            clean_environ(env)
            raise SetupSessionFailed('Could not create session !')
        self.session_id = identifier
        self.session_envs = env
        logger.debug('Session identifier is %s', identifier)
        logger.debug('Session environment variables: %s', env)
        logger.info('Configuration session is set up')
        return True

    def session_exists(self):
        """
        Test if a vyos config session is set up
        """
        return False if _run('{} inSession'.format(VYOS_SHELL_API)) else True

    def teardown_config_session(self):
        """
        End current configuration session.
        """
        if not self.session_exists():
            logger.warn('Teardown failed. No session available !')
            return False

        if not _run('{} teardownSession'.format(VYOS_SHELL_API)):
            logger.info('Cleaning up session environment variables')
            logger.info('Closing Vyos config session')
            clean_environ(self.session_envs)
            return True

        logger.error('Failed to teardown current config session')
        logger.warn('The Vyos config session may still open !')
        return False

    def session_changed(self):
        """
        Returns if Vyos configuration was changed from current session
        """
        if _run('{} sessionChanged'.format(VYOS_SHELL_API)):
            return False
        logger.warn('Vyos configuration was changed from current session')
        return True

    def commit(self):
        """
        Returns True if commit action succeed. False otherwise.
        """
        out = _run(os.path.join(VYOS_SBIN_DIR ,'my_commit'), output=True)
        if out == False:
            logger.error('Commit changes failed')
            raise OperationFailed('[ERROR] Commit changes failed !')
        logger.info('Changes successfully commited')
        return True

    def discard(self):
        """
        Undo config modifications
        """
        out = _run(os.path.join(VYOS_SBIN_DIR ,'my_discard'), output=True)
        if out == False:
            raise OperationFailed('[ERROR] Discard changes failed !')
        return out.splitlines()[0]

    def save(self):
        """
        Save applied modifications. Changes still persistent even after system reboot.
        """
        out = _run(os.path.join(VYOS_SBIN_DIR, VYOS_SAVE_SCRIPT), output=True)
        if out == False:
            logger.error('Saving changes failed')
            raise OperationFailed('[ERROR] Save changes failed !')
        logger.info('%s', out)
        return True
