#!/home/vyos/vyos-api/bin/python
import sys
sys.path.append('/home/vyos/vyos-api/')
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

    def show_dns(self,keys):
        pass

    def show_dhcp(self,keys):
        pass

    def show_nat(self,keys):
        try:
            print reduce(getitem,keys,self.serviceoutput)
        except KeyError:
            print 'no key available'
            
    def show_firewall(self,keys):
        pass

    def show_openvpn(self,keys):
        pass

    def show_interfaces(self,keys):
        pass

    def show_firewall(self,keys):
        pass

    def show_routing(self,keys):
        pass

    def show_webfiltering(self,keys):
        pass

obj = show_config('dns')
obj.show_nat(['forwarding','listen-on'])
