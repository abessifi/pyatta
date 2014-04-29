#!/usr/bin/env python
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from operations import configOpts
from validation import validation as vld

SDS = "service dhcp-server shared-network-name"

class dhcpHandler(configOpts):

    def dhcp_status(self,action,name):
        self.dhcp_config(action,[name,"disable"])

    def dhcp_config(self,action,suffix=[]):
        dhcp_params=[SDS]
        dhcp_params.extend(suffix)
        if action == 'delete':
            return self.delete(dhcp_params)
        return self.set(dhcp_params)

    def dhcp_dnsserver_default_router(self,action,service,name,subnet,addr):
        if service == 'default_router':
            suffix=["default-router",addr]
        elif service == "dns_server":
            suffix=["dns-server",addr]
        self.dhcp_subnet(action,name,subnet,suffix)
    
    def dhcp_subnet(self,action,name,subnet,suffix=[]):
        dhcp_params=[name,"subnet",subnet+"/24"]
        dhcp_params.extend(suffix)
        self.dhcp_config(action,dhcp_params)

    def set_range_adresses (self,name,subnet,adr_start,adr_stop):
        range=["start",adr_start,"stop",adr_stop]
        self.dhcp_subnet('set',name,subnet,range)



"""
obj=dhcpservice()
obj.setup_dhcp_default_router("Pool2","192.168.3.0","192.168.3.1")
obj.setup_dhcp_dns_server("Pool2","192.168.3.0","192.168.3.1")
obj.set_range_adresses("Pool2","192.168.3.0","192.168.3.100","192.168.3.200")
"""
