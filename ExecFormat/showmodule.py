#!/home/vyos/vyos-api/bin/python
import sys
sys.path.append('/home/vyos/vyos-api/project/')
from execformat import execUtils as executor
from VyosSessionConfig.configsession import ConfigSession as cs
from VyosSessionConfig.utils import logger
from VyosParser import vyos_parser as vparser
from pprint import pprint
from operator import getitem

class ServiceError(Exception): pass
class show_config():
    exe=executor()
    _args=['show']
    confsess=cs()
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
            print k.message
            print 'no key available'
