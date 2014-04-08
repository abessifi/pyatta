#!/home/vyos/vyos-api/bin/python

import pytest
import sys
import os
sys.path.append('/home/vyos/vyos-api/ServiceManager')
from ConfigInterfaces import configinterface as ifacecfg
import validation as vld

def test_ethernet_config():
    action=["set","delete"]
    for act in action:
        if act not in action: 
            with pytest.raises(vld.ActionError) as e :
                ifacecfg.ethernet_config(action)
            assert e.value.message == "[Critical] unrecognized action!"
 
def test_addr_interface():
    pass    

def test_hwid():
    pass

def test_iface_desc():
    pass

def ttest_fw_iface():
    pass

def test_vlan_desc():
    pass

def test_vlan_addr():
    pass

def test_del_vlan():
    pass

