#!/usr/bin/env python
import sys
import os
import logging
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from vyos_session import utils
from operations import configOpts
from validation import ActionError,  validation as vld
from execformat.formator import showConfig
from execformat.executor import session
from pprint import pprint

IE = "interfaces ethernet"
show=showConfig()
logger = logging.getLogger(__name__)
utils.init_logger(logger)

"""this class has to configure ethernet interfaces"""
class ifConfig(configOpts):
    orient=["in","out","local"]

    """this method allows you to setup or delete a specific configuration option"""
    def ethernet_config(self,action,suffix):
        iface_config=[IE]
        iface_config.extend(suffix)
        if action=="set":
            return self.set(iface_config)
        elif action=="delete":
            return self.delete(iface_config)
        else:
            raise ActionError("[Critical] unrecognized action!")

    def check_firewall_name(self,firewall):
        fw_names=show.formator(['firewall'])['name'].keys()
        if firewall not in fw_names:
            logger.error("%s way not match with any of the existing firewall\'s name!"%firewall)
            return False
        return True
        
    """this method may delete or set an ip address for a particular interface"""
    def addr_interface(self,action,interface,addr,vlan_label="",vlan_id=''):
        if  not vld.testip(addr):
            return False
        address = [interface,vlan_label,vlan_id,"address",addr+"/24"]
        self.ethernet_config(action,address)

    """this method may delete or set an MAC address for a particular interface"""
    def hw_id(self,action,interface,hwid):
        if not vld.testiface(interface):
            return False
        hw= [interface,"hw-id",hwid]
        self.ethernet_config(action,hw)

    """via this method, user can put a special description for desired interface """
    def iface_desc(self,action,interface,desc,vlan_label="",vlan_id=''):
        description = [interface,vlan_label,vlan_id,"description",desc]
        self.ethernet_config(action,description)

    """to set firewall rules for a specific interface, use the next method"""
    def firewall_to_iface(self,action,interface,orient,fwname):
        if orient not in self.orient:
            logger.error("%s: unrecognized orientation!"%orient)
            return False
        if not check_firewall_name(fwname):
            return False
        firewall=([interface,"firewall",orient,"name",fwname])
        self.ethernet_config(action,firewall)

    """try this method for adding descriptions to vlan sub interface"""
    def vlan_desc(self,action,interface,desc,vlan_id):
        self.iface_desc(action,interface,desc,"vif",vlan_id)

    """this method set an address for a vlan sub interface"""
    def vlan_addr(self,action,interface,addr,vlan_id):
        self.addr_interface(interface,addr,"vif",vlan_id)

    """this method can delete a vlan configuration on a particular interface"""
    def del_vlan(self,interface, vlan_id):
        if not str(vlan_id).digit():
            logger.error("%s:this given id can not be used as vlan id!"%vlan_id)
            return False
        vlan_fw = [interface,'vif',vlan_id]
        self.ethernet_config('delete',vlan)


"""
obj = configinterface()
obj.set_addr_interface("eth2","192.168.3.1")
obj.set_iface_desc("eth2","\"gateway for .3.0/24\"")
obj.set_vlan_desc("eth2","VLAN3","30")
obj.set_vlan_addr("eth2","192.168.30.1","20")
"""

