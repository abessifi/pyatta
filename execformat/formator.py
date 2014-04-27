#!/usr/bin/env python
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from executor import session, OperationFailed,execUtils as executor
from vyos_session.utils import logger
from vyosparser import vyos_parser as vparser
from pprint import pprint
from operator import getitem

class ServiceError(Exception): pass

args=['show']

class showConfig():
    exe=executor()
    serviceoutput=""
    
    #def __init__(self):
        #session.setup_config_session()
        #self.serviceoutput=self.show_all(service)
        
    def formator(self,options):
        service = options[0]
        
        if service in ['protocols','nat','interfaces','firewall']:
           args.extend(options)
        elif service in ['dns','dhcp-server','ssh','webproxy']:
            options.insert(0,'service')
            args.extend(options)
        else:
            raise ServiceError('unknown such service!')
        try:
            #if not exe.checkcmd(' '.join(args)):
             #   logger.error("%s: given args does not match with existing configs!"%args)
              #  return False
	        execstate,output=self.exe.execmd(args)
        except OperationFailed, e:
            logger.error(e.message)
            return False
        if execstate==True:
            return vparser.decode_string(output)
        #session.teardown_config_session()


    """
    def customized_show(self,keys):
        try:
            return reduce(getitem,keys,self.serviceoutput)
        except KeyError,k:
            return {k.message:'no such available key'}
    """
#obj=showConfig()
#print obj.formator(['firewall','name33','svs'])
