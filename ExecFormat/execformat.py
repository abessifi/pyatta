import sys
import subprocess
import os

sys.path.append('/home/vyos/vyos-api/')
from VyosSessionConfig import configsession as cs
from VyosSessionConfig import utils

logger = utils.logger

VYOS_SBIN_DIR = utils.get_config_params('bin','vyos_sbin_dir')
VYOS_SHELL_API = utils.get_config_params('bin', 'shell_api_path')

class OperationFailed(Exception): pass
class OperationNameError(Exception): pass

def check_operation_name(args):
    """
    Check if operation/command name is correct.
    """
    if len(args) == 0:
        logger.error('Operation name required')
        raise OperationNameError('Operation name required.')
    elif args[0] not in ['show','set','delete']:
        logger.error('Operation name "%s" not correct' % args[0])
        raise OperationNameError('Operation name not correct.')
    return True

class execUtils:
    """
    Executes possible operations in a Vyos configure session.
    """

    def execmd(self, args):
        """
        Performs execution of allowed config operations ['show','set','delete']
        """
        if check_operation_name(args):
            # prepare executable file to be called
            operation_name = args[0]
            logger.info('Perform operation "%s"' % operation_name)
            if args[0] == 'show': args[0] = '{} showCfg'.format(VYOS_SHELL_API)
            else: args[0] = os.path.join(VYOS_SBIN_DIR, 'my_{}'.format(args[0]))
            logger.debug('exec command: %s' % ' '.join(args))
            # NOTE:
            # if Popen(args, shell=True, ...) => Execution fails
            # if Popen(args, ...) => OSError: [Errno 2] No such file or directory
            # if args = ['/bin/cli-shell-api','showCfg', ...] and Popen(args, ...) that works but actually we keep using ' '.join(args).
            proc = subprocess.Popen(' '.join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # wait for the process to terminate and get stdout/stderr outputs
            out, err = proc.communicate()
            errcode = proc.returncode

            logger.debug('command return code: %s' % errcode)
            
            if errcode:
                logger.info('command output: %s' % ' '.join(out.splitlines()))
                logger.error('Failed executing operation "%s"' % operation_name)
                raise OperationFailed('Operation failed !')    
            logger.debug('%s' % ' '.join(out.splitlines()))
            logger.info('Executing "%s" operation OK' % operation_name)
            return (True, out)

    def discover_possible_ops():
        """
        Returns possible config path that corresponds to an allowed operation
        """
        pass
