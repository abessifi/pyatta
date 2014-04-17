#!/home/vyos/vyos-api/bin/python
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from execformat import execUtils as executor
from VyosSessionConfig.utils import logger
from VyosParser import vyos_parser as vparser
from pprint import pprint
from operator import getitem

class ServiceError(Exception): pass
class show_config():
    exe=executor()
    _args=['show']
    serviceoutput=""
    def __init__(self,service):
        self.serviceoutput=self.show_all(service)
        
    def show_all(self,service):
        if service in ['protocols','nat','interfaces','firewall']:
           self._args.append(service)
        elif service in ['dns','dhcp-server','ssh','webproxy']:
            self._args.extend(['service',service])
        else:
            raise ServiceError('unknown such service!')
        try:
            execstate,output=self.exe.execmd(self._args)
            if execstate==True:
                return vparser.decode_string(output)
        except OperationFailed, e:
            logger.error(e.message)

    def customized_show(self,keys):
        try:
            return reduce(getitem,keys,self.serviceoutput)
        except KeyError,k:
            return {k.message:'no such available key'}

#obj=show_config('nat')
#pprint(obj.serviceoutput)
#pprint(obj.customized_show(['source','rule']))
