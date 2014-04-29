#!/usr/bin/env python
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from executor import OperationFailed, execUtils as executor
from vyos_session.utils import logger
from vyosparser import vyos_parser as vparser

class ServiceError(Exception): pass
args=['show']

class showConfig():
        
    def formator(self,options):
        service = options[0]
        if service in ['protocols','nat','interfaces','firewall']:
           args.extend(options)
        elif service in ['dns','dhcp-server','ssh','webproxy']:
            options.insert(0,'service')
            args.extend(options)
        else:
            raise ServiceError('unknown such service!')
        exe=executor(list(args))
        try:
            #if not exe.checkcmd(' '.join(args)):
             #   logger.error("%s: given args does not match with existing configs!"%args)
              #  return False
	        execstate,output=exe.execmd()
        except OperationFailed, e:
            logger.error(e.message)
            return False
        if execstate==True:
            return vparser.decode_string(output)


