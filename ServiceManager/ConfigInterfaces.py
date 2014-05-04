#!/usr/bin/env python
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from ConfigOpt import config_opt
import validation as vld

IE = "interfaces ethernet"

"""this class has to configure ethernet interfaces"""
class  configinterface(config_opt):
    orient=["in","out","local"]

    """this method allows you to setup or delete a specific configuration option"""
    def ethernet_config(self,action,suffix):
        iface_config=[IE]
        iface_config.extend(suffix)
        if action=="set":
            self.set(iface_config)
        elif action=="delete":
            self.delete(iface_config)
        else:
            raise vld.ActionError("[Critical] unrecognized action!")

    """this method may delete or set an ip address for a particular interface"""
    def addr_interface(self,action,interface,addr,vlan_label="",vlan_id=''):
        address = [interface,vlan_label,vlan_id,"address",addr+"/24"]
        self.ethernet_config(action,address)

    """this method may delete or set an MAC address for a particular interface"""
    def hw_id(self,action,interface,hwid):
        hw= [interface,"hw-id",hwid]
        self.ethernet_config(action,hw)

    """via this method, user can put a special description for desired interface """
    def iface_desc(self,action,interface,desc,vlan_label="",vlan_id=''):
        description = [interface,vlan_label,vlan_id,"description",desc]
        self.ethernet_config(action,description)

    """to set firewall rules for a specific interface, use the next method"""
    def firewall_to_iface(self,action,interface,orient,fwname):
        firewall=[interface,"firewall"]
        if action == 'set':
            if orient in self.orient:
                firewall.extend([orient,"name",fwname])
            else:
                return "unrecognized orientation!" 
        self.ethernet_config(action,firewall)

    """try this method for adding descriptions to vlan sub interface"""
    def vlan_desc(self,action,interface,desc,vlan_id):
        self.iface_desc(action,interface,desc,"vif",vlan_id)

    """this method set an address for a vlan sub interface"""
    def vlan_addr(self,action,interface,addr,vlan_id):                  
        self.addr_interface(interface,addr,"vif",vlan_id)

    """this method can delete a vlan configuration on a particular interface"""
    def del_vlan(self,interface,vlan_id):
        vlan = [interface,'vif',vlan_id]
        self.ethernet_config('delete',vlan)

"""
obj = configinterface()
obj.set_addr_interface("eth2","192.168.3.1")
obj.set_iface_desc("eth2","\"gateway for .3.0/24\"")
obj.set_vlan_desc("eth2","VLAN3","30")
obj.set_vlan_addr("eth2","192.168.30.1","20")
"""

