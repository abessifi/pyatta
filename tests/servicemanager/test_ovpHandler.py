#!/usr/bin/env python

import pytest
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from execformat.executor import session
from vyos_session import configsession as vsc
from servicemanager import ovp_handler as OV
from servicemanager import validation as vld

vpn = OV.ovpHandler()
valid=vld.validation()

def setup_module(module):
    """
    Set up a config session
    """
    session.setup_config_session()

def teardown_module(module):
    """
    Teardown created config session
    """
    session.teardown_config_session()

def test_ipaddrvalidation():
    Erraddr = ["123.123.123","456.234.123.123","sfd.213.d.23"]
    for addr in Erraddr:
        assert valid.testip(addr)==False
    assert valid.testip('223.13.123.123')==True

def test_interfacevalidation():
    assert valid.testiface('eth0') == True
    assert valid.testiface('eth5') == False

def test_addressvalidation():
    assert valid.addrvalidation('10.1.1.1') == True
    assert valid.addrvalidation('192.168.1.50') == False

def test_checkinterface():
    assert valid.testiface('vtun0')==True
    assert valid.testiface('vtun1')==False

def test_sharedkey():
    if  os.path.exists('/config/auth/cleee')==False:
        assert vpn.shared_keygen('cleee') == True
        assert os.path.exists('/config/auth/cleee') and os.path.isfile('/config/auth/cleee')==True

def test_openvpn_config():
    assert vpn.openvpn_config('vtun0','set',["tls","role","passive"]) == True
    assert vpn.openvpn_config('vtun0','set',["blabla","role","passive"])==False

def test_set_interface():
    with pytest.raises(OV.InterfaceExist) as e:
        vpn.set_interface_vpn('vtun0')
    assert e.value.message == "[WORNING] interface already exist"
def test_local_remote_vaddr():
    assert vpn.endpoint_local_remote_vaddr('set','local','vtun0','10.1.1.1')==True
    assert vpn.endpoint_local_remote_vaddr('set','blabla','vtun0','10.1.1.1')==False
    assert vpn.endpoint_local_remote_vaddr('set','remote','vtun1','10.1.1.1')==True
    assert vpn.endpoint_local_remote_vaddr('set','local','vtun0','333.1.1.1')==False

def test_modevpn():
    listmode=['client','server','site-to-site']
    for mode in listmode:
        assert vpn.vpn_mode('set','vtun0',mode)==True
    if mode not in listmode:
        with pytest.raises(OV.ModeError) as e :
            vpn.vpn_mode('set','vtun0',mode)
        assert e.value.message == '[ERROR] valid mode is required !'

def test_remotelocal_host():
    assert vpn.define_local_remote_host('set','vtun0','local','10.1.1.1')==True
    assert vpn.define_local_remote_host('set','vtun0','remote','192.168.1.250')==True
    assert vpn.define_local_remote_host('set','vtun0','blabla','192.168.1.250')==False
    with pytest.raises(vld.AddressError) as e :
        vpn.define_local_remote_host('set','vtun0','local','192.168.1.250')
    assert e.value.message == "No such address already configured locally!"    

def test_sharedkey_path():
    assert vpn.sharedkey_file_path('set','vtun0','/config/auth/cleee')==True
    assert vpn.sharedkey_file_path('set','vtun0','/config/auth/blaa')==False

def test_route_vpn():
    assert vpn.access_route_vpn('set','vtun0','192.168.1.0')==True

def test_rolevpn():
    listroles=['active','passive']
    for role in listroles:
        assert vpn.tls_role('set','vtun0',role)==True
    if role not in listroles:
        with pytest.raises(OV.RoleError) as e :
            vpn.vpn_mode('set','vtun0',role)
        assert e.value.message == '[ERROR] unvalid role: possible choice:active, passive'

def test_keyspath_path():
    assert vpn.tls_files('set','vtun0','/config/auth/ca.crt')==True
    assert vpn.tls_files('set','vtun0','/config/auth/vyos-server.crt')==True
    assert vpn.tls_files('set','vtun0','/config/auth/blabla.pem')==False
    with pytest.raises(OV.FileError) as e :
        vpn.tls_files('set','vtun0','/config/auth/serial.old')
    assert e.value.message == "/config/auth/serial.old: invalid file type!"

def test_encryption_algo():
    algo_cipher=["des","3des","bf256","aes128","aes256"]
    for algo in algo_cipher:
        assert vpn.encryption_algorithm('set','vtun0',algo)==True
    if algo not in algo_cipher:
        with pytest.raises(OV.CipherError) as e :
            vpn.encryption_algorithm('set','vtun0',algo)
        assert e.value.message == "[ERROR] %s is not a valid ancryption algorithm!" %algo
    
def test_localport():
    assert vpn.local_port('set','vtun0','1234')==True
    with pytest.raises(OV.LocalportError) as e :
        vpn.local_port('set','vtun0','1234333')
        vpn.local_port('set','vtun0','1vfsd')
    assert e.value.message == "[ERROR] port number expected is false, 1194 is recommanded"
