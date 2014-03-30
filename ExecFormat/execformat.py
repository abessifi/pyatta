import sys
import subprocess
import os
import logging

sys.path.append('/home/vyos/vyos-api/project')
from VyosSessionConfig import configsession as cs
from VyosSessionConfig import utils

VYOS_SBIN_DIR = utils.get_config_params('bin','vyos_sbin_dir')
VYOS_SHELL_API = utils.get_config_params('bin', 'shell_api_path')

class OperationFailed(Exception): pass
class OperationNameError(Exception): pass

def check_operation_name(args):
    """
    Check if operation/command name is correct.
    """
    if len(args) == 0:
        raise OperationNameError('[ERROR] Operation name required.')
    elif args[0] not in ['show','set','delete']:
        raise OperationNameError('[ERROR] Operation name not correct.')
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
            if args[0] == 'show': args[0] = '{} showCfg'.format(VYOS_SHELL_API)
            else: args[0] = os.path.join(VYOS_SBIN_DIR, 'my_{}'.format(args[0]))
            # NOTE:
            # if Popen(args, shell=True, ...) => Execution fails
            # if Popen(args, ...) => OSError: [Errno 2] No such file or directory
            # if args = ['/bin/cli-shell-api','showCfg', ...] and Popen(args, ...) that works but actually we keep using ' '.join(args).
            proc = subprocess.Popen(' '.join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # wait for the process to terminate and get stdout/stderr outputs
            out, err = proc.communicate()
            errcode = proc.returncode
            if errcode:
                # TODO log %err% output
                raise OperationFailed('[ERROR] Operation failed !')    
            return (True, out)

    def discover_possible_ops():
        """
        Returns possible config path that corresponds to an allowed operation
        """
        pass
