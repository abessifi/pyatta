#!/usr/bin/env python

"""this class implements the necessary fonctionnalities to setup 
an openvpn service in both site-to-site and server-client mode"""
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)

from operations import configOpts
from routing_handler import routingHandler
import validation as validate
from validation import validation as vld
from subprocess import check_output,CalledProcessError

class CipherError(Exception): pass
class LocalportError(Exception): pass
class ProtocolError(Exception): pass
class KeyfileError(Exception): pass
class ModeError(Exception): pass
class InterfaceExist(Exception): pass
IOV="interfaces openvpn"

class ovpHandler(configOpts):
    RS = routingHandler()
    algo_cipher=["des","3des","bf256","aes128","aes256"]
    protocol=["udp","tcp-passive","tcp-active"]
    keyfiles=["ca-cert","cert","dh","key"]
    role=["active","passive"]
    mode=["server","client","site-to-site"]

    @staticmethod
    def shared_keygen(sharedkeyname):
        try:
            check_output("/usr/sbin/openvpn --genkey --secret /config/auth/"+sharedkeyname ,shell=True)
            return True
        except CalledProcessError as e:
            print ("[Critical] Sth wrong has been occurred ! execution fails with return code %s" % e.returncode)
            return False

    """this method have to restructure any command line and pass it to the executor"""
    def openvpn_config(self,iface,action,suffix=[]):
        openvpn_params=[IOV,iface]
        openvpn_params.extend(suffix)
        if action=='set':
            return  self.set(openvpn_params)
        elif action=='delete':
            return self.delete(openvpn_params)
        else:
            return 'unknown operation!',action

    """this method grant a new virtual interface to 
    endpoint participant in openvpn connection"""
    def set_interface_vpn(self,iface):
        if vld.testiface(iface):
            raise InterfaceExist("[WORNING] interface already exist")
        return self.openvpn_config(iface,action)

    """this method accord a local address for openvpn interface in site-to-site mode"""
    def endpoint_local_vaddr(self,action,iface,local_vaddr):
        if vld.testiface(iface) and vld.testip(local_vaddr):
            suffix=["local-address",local_vaddr]
            return self.openvpn_config(iface,action,suffix)

    """this method allow openvpn endpoints to act on a specific mode"""
    def vpn_mode(self,action,iface,mode):
        if vld.testiface(iface):
            if mode not in self.mode:
                raise ModeError("[ERROR] valid mode is required !")
            suffix=["mode",mode]
            return self.openvpn_config(iface,action,suffix)

    """this method accord a local address for openvpn interface in site-to-site mode"""
    def endpoint_remote_vaddr(self,action,iface,remote_vaddr):
        if vld.testiface(iface) and vld.testip(remote_vaddr):
            suffix=["remote-address",remote_vaddr]
            return self.openvpn_config(iface,action,suffix)

    """this method is used in both site-to-site and client-server mode,
        and let the passive endpoint to know the physical address of the active one"""
    def define_remotelocal_host(self,action,iface,pos,host):
        if vld.testiface(iface):
            if (pos == 'local' and vld.addrvalidation(host)) or pos == 'remote':
                suffix=[pos+"-host",host]
                return self.openvpn_config(iface,action,suffix)
            elif pos not in ['remote','local']:
                return "[ERROR] unvalid host position"
            else:
                raise validate.AddressError("No such address already configured!")

    """this method have to define the right path to reach shared 
    key file on a site-to-site connection"""
    def sharedkey_file_path(self,action,iface,path):
        if vld.testiface(iface):
            if vld.testpath(path):                
                suffix=["shared-secret-key-file",path]
                return self.openvpn_config(iface,action,suffix)

    #look at action handler in RoutingService.py
    """this method create the static route to access the remote 
    subnet via the openvpn tunnel in a site-to-site mode"""
    def access_route_vpn(self,action,iface,dst_subnet):
        if vld.testiface(iface) and vld.testip(dst_subnet):
            self.RS.set_interface_route(dst_subnet,iface)
            return True

    """this method specify a specific role (passive,active) for an endpoint in tls mode"""
    def tls_role(self,action,iface,role):
        if vld.testiface(iface):
            if role not in self.role:
                raise RoleError("[ERROR] unvalid role: possible choice:active, passive")
            suffix=["tls role",role]
            return self.openvpn_config(iface,action,suffix)

    """this method specify the locations of all files used 
    to establish a vpn connection in client-server mode"""
    def define_files(self,action,iface,typefile,abspath):
        if vld.testiface(iface):
            if typefile not in self.keyfiles:
                raise KeyfileError("[ERROR] unvalid keyfile type!")
            elif vld.testpath(abspath):
                suffix=["tls",typefile+"-file",abspath]
                return self.openvpn_config(iface,action,suffix)

    """this method has the ability to delete an openvpn 
    interface with its appropriate configuration """
    def del_vpn_config(self,iface):
        if vld.testiface(iface):
            return self.delete('delete',[IOV,iface])

    """in client-server mode, this method is able to 
    specify the subnet for the openvpn tunnel """
    def server_range_addr(self,action,iface,subnet):
        if vld.testiface(iface) and vld.testip(subnet):
            suffix=["server subnet",subnet+"/24"]
            return self.openvpn_config(iface,action,suffix)

    """this method set a route on the server that will be pushed 
    to all clients during the connection establishment"""
    def push_root_subnet(self,action,iface,subnet):
        if vld.testiface(iface) and vld.testip(subnet):
            suffix=["server push-route",subnet+"/24"]
            return self.openvpn_config(iface,action,suffix)

    """as far as the previous method,this on set a route on the server that 
    will be pushed to all clients during the connection establishment"""
    def push_root_nameserver(self,action,iface,nameserver):
        if vld.testiface(iface) and vld.testip(nameserver):
            suffix=["server name-server",nameserver]
            return self.openvpn_config(iface,action,suffix)

    """setup the data encryption algorithm"""
    def encryption_algorithm(self,action,iface,algorithm):
        if vld.testiface(iface):
            if algorithm in self.algo_cipher:
                suffix=["encryption",algorithm]               
                return self.openvpn_config(iface,action,suffix)
            else:
                raise CipherError("[ERROR] %s is not a valid ancryption algorithm!" %algorithm)

    """define the local port number in the server to accept remote connctions"""
    def local_port(self,action,iface,port):
        if vld.testiface(iface):
            if str(port).isdigit() and (1024 < int(port) < 36565):
                suffix=["local-port",port]
            else:
                raise LocalportError("[ERROR] port number expected is false, 1194 is recommanded")
            return self.openvpn_config(iface,action,suffix)
    
    """specify the openvpn communication protocol"""
    def communication_protocol(self,action,iface,prot):
        if vld.testiface(iface):
            if prot in self.protocol:
                suffix=["protocol"]
                suffix.append(prot)
            else:
                raise ProtocolError("[ERROR] %s can not be used as OpenVPN communication protocol! udp was set by default" %prot)
            return self.openvpn_config(iface,action,suffix)

    """this method allow the user to add openvpn options that 
    are not supported by the vyatta configuration yet"""
    def additional_options(self,action,iface,options):
        if vld.testiface(iface):
            suffix = ["openvpn-option",options]
            return self.openvpn_config(iface,action,suffix)


"""
obj=openvpn()
obj.set_interface_vpn("0")
obj.set_vpn_mode("0","server")
obj.set_server_range_addr("0","10.1.1.0")
obj.push_root_subnet("0","172.168.1.0")
obj.define_files("0","ca-cert","/config/auth/ca.crt")
obj.define_files("0","cert","/config/auth/vyos-server.crt")
#obj.define_files("0","crl","/config/auth/01.pem")
obj.define_files("0,"dh","/config/auth/dh1024.pem")
obj.define_files("0","key","/config/auth/vyos-server.key")
obj.exe.commit()
obj.exe.save()
"""
#obj.set_endpoint_local_vaddr("0","192.168.100.1")
#obj.set_endpoint_remote_vaddr("0","192.168.100.2")
#obj.define_remote_host("0","172.168.1.22")
#obj.sharedkey_file_path("0","/config/auth/zomta3key")
#obj.set_access_route_vpn("0","192.168.1.0")
#obj.del_vpn_iface("0")
