
#!/home/vyos/vyos-api/bin/python

import pytest
import sys
import os
sys.path.append('/home/vyos/vyos-api/')
from ServiceManager import OpenVPN as OV
from ServiceManager import validation as vld

vpn = OV.openvpn()
valid=vld.validation()

def test_ipaddrvalidation():
    Erraddr = ["123.123.123","456.234.123.123","sfd.213.d.23"]
    for addr in Erraddr:
        assert valid.ipvalidation(addr)==False
    assert valid.ipvalidation('223.13.123.123')==True
    
def test_interfacevalidation():
    assert valid.ifacevalidation('eth0') == True
    assert valid.ifacevalidation('eth5') == False

def test_addressvalidation():
    assert valid.addrvalidation('10.1.1.1') == True
    assert valid.addrvalidation('192.168.1.50') == False

def test_checkinterface():
    assert valid.testiface('vtun0')==True
    with pytest.raises(vld.InterfaceError) as e :
        valid.testiface('vtun1')
    assert e.value.message == '[ERROR] invalid interface'

def test_sharedkey():
    if  os.path.exists('/config/auth/cleee')==False:
        assert vpn.shared_keygen('cleee') == True
        assert os.path.exists('/config/auth/cleee') and os.path.isfile('/config/auth/cleee')==True

def test_openvpn_config():
    assert vpn.openvpn_config('0',["server","role","passive"]) == "interfaces openvpn vtun0 server role passive"

def test_set_interface():
    with pytest.raises(OV.InterfaceExist) as e :
        vpn.set_interface_vpn('0')
    assert e.value.message == '[WORNING] interface already exist' 

def test_set_local_vaddr():
    assert vpn.set_endpoint_local_vaddr('0','10.1.1.1')==True
    with pytest.raises(vld.InterfaceError) as e :
        vpn.set_endpoint_local_vaddr('1','10.1.1.1')
    assert e.value.message == '[ERROR] invalid interface'
    with pytest.raises(vld.IpformatError) as e :
        vpn.set_endpoint_local_vaddr('0','333.1.1.1')
    assert e.value.message == '[ERROR] invalid ip address'

def test_modevpn():
    listmode=['client','server','site-to-site']
    for mode in listmode:
        assert vpn.set_vpn_mode('0',mode)==True
    if mode not in listmode:
        with pytest.raises(OV.ModeError) as e :
            vpn.set_vpn_mode('0',mode)
        assert e.value.message == '[ERROR] valid mode is required !'

def test_remotelocal_host():
    assert vpn.define_remotelocal_host('0','local','10.1.1.1')==True
    assert vpn.define_remotelocal_host('0','remote','192.168.1.250')==True
    assert vpn.define_remotelocal_host('0','blabla','192.168.1.250')=="[ERROR] unvalid host position"
    with pytest.raises(vld.AddressError) as e :
        vpn.define_remotelocal_host('0','local','192.168.1.250')
    assert e.value.message == "No such address already configured!"    

def test_sharedkey_path():
    assert vpn.sharedkey_file_path('0','/config/auth/cleee')==True
    with pytest.raises(vld.PathError) as e :
        vpn.sharedkey_file_path('0','/config/auth/blaa')
    assert e.value.message == "[ERROR] check your input path file"

def test_route_vpn():
    assert vpn.set_access_route_vpn('0','192.168.1.0')==True

def test_rolevpn():
    listroles=['active','passive']
    for role in listroles:
        assert vpn.set_tls_role('0',role)==True
    if role not in listroles:
        with pytest.raises(OV.RoleError) as e :
            vpn.set_vpn_mode('0',role)
        assert e.value.message == '[ERROR] unvalid role: possible choice:active, passive'

def test_keyspath_path():
    keyfilelist=["ca-cert","cert","dh","key"]
    for keyfile in keyfilelist:
        assert vpn.define_files('0',keyfile,'/config/auth/cleee')==True
    if keyfile not in keyfilelist:
        with pytest.raises(OV.KeyfileError) as e :
            vpn.define_files('0',keyfile,'/config/auth/blaaa')
        assert e.value.message=="[ERROR] unvalid keyfile type!"
    else:
        with pytest.raises(vld.PathError) as e :
            vpn.define_files('0',keyfile,'/config/auth/blaa')
        assert e.value.message == "[ERROR] check your input path file"

def test_server_subnet():
    algo_cipher=["des","3des","bf256","aes128","aes256"]
    for algo in algo_cipher:
        assert vpn.set_encryption_algorithm('0',algo)==True
    if algo not in algo_cipher:
        with pytest.raises(OV.CipherError) as e :
            vpn.set_encryption_algorithm('0',algo)
        assert e.value.message == "[ERROR] %s is not a valid ancryption algorithm!" %algo
    
def test_localport():
    assert vpn.set_local_port('0','1234')==True
    with pytest.raises(OV.LocalportError) as e :
        vpn.set_local_port('0','1234333')
        vpn.set_local_port('0','1vfsd')
    assert e.value.message == "[ERROR] port number expected is false, 1194 is recommanded"
