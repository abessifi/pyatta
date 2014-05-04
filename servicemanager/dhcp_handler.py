#!/usr/bin/env python
import sys
import os
import logging
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from operations import configOpts
from validation import validation as vld
from execformat.formator import showConfig
from vyos_session import utils
from execformat.executor import session
from pprint import pprint

SDS = "service dhcp-server shared-network-name"
show=showConfig()
logger = logging.getLogger(__name__)
utils.init_logger(logger)

class dhcpHandler(configOpts):

    def get_subnet_from_name(self,dhcp_name):
        subnet_mask = (show.formator(['dhcp-server','shared-network-name',dhcp_name])['subnet'].keys())
        subnet=subnet_mask[0].split('/')[0]
        return subnet
        #return (show.formator(['dhcp-server'])['shared-network-name'][dhcp_name]['subnet'].keys())[0].split('/')[0]
            #logger.error("%s subnet does not match with that was set for %s configs"%(subnet,dhcp_name))
            #return False
        #return True

    def check_dhcp_name(self,dhcp_name):
        dhcp_names=show.formator(['dhcp-server'])['shared-network-name'].keys()
        if dhcp_name not in dhcp_names:
            logger.warn("%s in not a valid name for an existing dhcp config!"%dhcp_name)
            return False
        return True

    def dhcp_status(self,action,name):
        return self.dhcp_config(action,[name,"disable"])

    def dhcp_config(self,action,suffix=[]):
        dhcp_params=[SDS]
        dhcp_params.extend(suffix)
        if action == 'delete':
            return self.delete(dhcp_params)
        elif action == 'set':
            print dhcp_params
            print action
            #return self.set(dhcp_params)

    def dhcp_dnsserver_default_router(self,action,service,name,addr):
        if not vld.testip(addr) or not vld.addrvalidation(addr):
            return False
        if service == 'default_router':
            suffix=["default-router",addr]
        elif service == "dns_server":
            suffix=["dns-server",addr]
        subnet=self.get_subnet_from_name(name)
        return self.dhcp_subnet(action,name,subnet,suffix)
    
    def dhcp_subnet(self,action,name,subnet="",suffix=[]):
        dhcp_params=[name]
        if subnet:
            if not vld.testip(subnet):
                return False
            dhcp_params.extend(["subnet",subnet+"/24"]+suffix)
        return self.dhcp_config(action,dhcp_params)

    def set_range_adresses (self,name,subnet,adr_start,adr_stop):
        if not vld.testip(subnet) or not vld.testip(adr_start) or not vld.testip(adr_stop):
            return False
        range=["start",adr_start,"stop",adr_stop]
        return self.dhcp_subnet('set',name,subnet,range)


"""
obj=dhcpHandler()
session.setup_config_session()
#print obj.check_dhcp_name('Pool3')
print obj.check_subnet_from_name('Pool3')
#obj.dhcp_subnet('delete','Pool3')
#obj.set_range_adresses('Pool3','192.168.1.0','192.168.1.100','192.168.1.200')
#obj.dhcp_dnsserver_default_router('delete','default_router','Pool3','192.168.1.0','192.168.1.3')
#obj.dhcp_dnsserver_default_router('delete','dns_server','Pool3','192.168.1.0','192.168.1.3')
#obj.dhcp_status('set','Pool3')
#session.commit()
session.teardown_config_session()


obj=dhcpservice()
obj.setup_dhcp_default_router("Pool2","192.168.3.0","192.168.3.1")
obj.setup_dhcp_dns_server("Pool2","192.168.3.0","192.168.3.1")
obj.set_range_adresses("Pool2","192.168.3.0","192.168.3.100","192.168.3.200")
"""
