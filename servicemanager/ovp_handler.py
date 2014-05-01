#!/usr/bin/env python

"""this class implements the necessary fonctionnalities to setup 
an openvpn service in both site-to-site and server-client mode"""
import sys
import os
import logging
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)

from vyos_session import utils
from operations import configOpts
from routing_handler import routingHandler
import validation as validate
from validation import AddressError, validation as vld
from subprocess import check_output,CalledProcessError

class CipherError(Exception): pass
class LocalportError(Exception): pass
class ProtocolError(Exception): pass
class FileError(Exception): pass
class ModeError(Exception): pass
class RoleError(Exception): pass
class InterfaceExist(Exception): pass

IOV="interfaces openvpn"
logger = logging.getLogger(__name__)
utils.init_logger(logger)

class ovpHandler(configOpts):
    RS = routingHandler()
    pos=['local','remote']
    algo_cipher=["des","3des","bf256","aes128","aes256"]
    protocol=["udp","tcp-passive","tcp-active"]
    role=["active","passive"]
    mode=["server","client","site-to-site"]

    """this method check if a given openvpn interface name has a correct format or not"""
    def check_ovp_iface_name(self,iface):
        return True if iface[:4] =='vtun' and str(iface[4:]).isdigit() else False

    @staticmethod
    def shared_keygen(sharedkeyname):
        try:
            check_output("/usr/sbin/openvpn --genkey --secret /config/auth/"+sharedkeyname ,shell=True)
            return True
        except CalledProcessError as e:
            logger.error("Sth wrong has been occurred ! execution fails with return code %s" % e.returncode)
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
            logger.warn("interface %s already exist"%iface)
            raise InterfaceExist("[WORNING] interface already exist")
        elif not self.check_ovp_iface_name(iface):
            logger.error("%s is not in the correct format!"%iface)
            return False
        return self.openvpn_config(iface,'set')

    """this method accord a local and remote address for openvpn interface in site-to-site mode"""
    def endpoint_local_remote_vaddr(self,action,pos,iface,vaddr):
        if not vld.testip(vaddr) or pos not in self.pos:
            return False
        suffix=[pos+"-address",vaddr]
        return self.openvpn_config(iface,action,suffix)

    """this method allow openvpn endpoints to act on a specific mode"""
    def vpn_mode(self,action,iface,mode):
        if mode not in self.mode:
            logger.error("%s is not a valid mode!"%mode)
            raise ModeError("valid mode is required !")
        suffix=["mode",mode]
        return self.openvpn_config(iface,action,suffix)

    """this method is used in both site-to-site and client-server mode,
        and let the passive endpoint to know the physical address of the active one"""
    def define_local_remote_host(self,action,iface,pos,host):
        if pos not in self.pos:
            logger.error("given pos %s is not valid!"%pos)
            return False
        if (pos == 'local' and vld.addrvalidation(host)) or pos == 'remote':
            suffix=[pos+"-host",host]
            return self.openvpn_config(iface,action,suffix)
        else:
            raise AddressError("No such address already configured locally!")

    """this method have to define the right path to reach 
    pre shared secret file on a site-to-site connection"""
    def sharedkey_file_path(self,action,iface,path):
        if not vld.testpath(path):
            return False         
        suffix=["shared-secret-key-file",path]
        return self.openvpn_config(iface,action,suffix)

    #look at action handler in RoutingService.py
    """this method create the static route to access the remote 
    subnet via the openvpn tunnel in a site-to-site mode"""
    def access_route_vpn(self,action,iface,dst_subnet):
        if not vld.testip(dst_subnet):
            return False
        self.RS.set_interface_route(dst_subnet,iface)
        return True

    """this method specify a specific role (passive,active) for an endpoint in tls mode"""
    def tls_role(self,action,iface,role):
        if role not in self.role:
            logger.error("invalid role %s:possible choice:active, passive!"%role)
            raise RoleError("invalid role: possible choice:active, passive")
        suffix=["tls role",role]
        return self.openvpn_config(iface,action,suffix)

    """this method specify the locations of all files used 
    to establish a vpn connection in client-server mode"""
    def tls_files(self,action,iface,abspath):
        if not vld.testpath(abspath):
            return False
        suffix=['tls']
        file_name=abspath.split('/')[-1].split('.')[0]
        file_ext=abspath.split('.')[-1]
        if file_ext=='crt':
            if file_name != 'ca':
                keyfile='cert-file'
            keyfile='ca-cert-file'
        elif file_ext=='key':
            keyfile='key-file'
        elif file_ext=='pem':
            keyfile='dh-file'
        else:
            logger.error("%s: invalid file type!"%abspath)
            raise FileError("%s: invalid file type!"%abspath)
        suffix.extend([keyfile,abspath])
        return self.openvpn_config(iface,action,suffix)

    """this method has the ability to delete an openvpn 
    interface with its appropriate configuration """
    def del_vpn_config(self,iface):
        if not vld.testiface(iface):
            logger.error("%s does not exists in the current mounted interfaces!"%iface)
            return False
        return self.delete('delete',[IOV,iface])
    """in client-server mode, this method is able to 
    specify the subnet for the openvpn tunnel """
    def server_range_addr(self,action,iface,subnet):
        if not vld.testip(subnet):
            return False
        suffix=["server subnet",subnet+"/24"]
        return self.openvpn_config(iface,action,suffix)

    """this method set a route on the server that will be pushed 
    to all clients during the connection establishment"""
    def push_route_subnet(self,action,iface,subnet):
        if not vld.testip(subnet):
            return False
        suffix=["server push-route",subnet+"/24"]
        return self.openvpn_config(iface,action,suffix)

    """as far as the previous method,this one set a nameserver on the server that 
    will be pushed to all clients during the connection establishment"""
    def push_root_nameserver(self,action,iface,nameserver):
        if not vld.testip(nameserver):
            return False
        suffix=["server name-server",nameserver]
        return self.openvpn_config(iface,action,suffix)

    """setup the data encryption algorithm"""
    def encryption_algorithm(self,action,iface,algorithm):
        if algorithm not in self.algo_cipher:
            logger.error("%s is not a valid ancryption algorithm!" %algorithm)
            raise CipherError("[ERROR] %s is not a valid ancryption algorithm!" %algorithm)
        suffix=["encryption",algorithm]               
        return self.openvpn_config(iface,action,suffix)

    """define the local port number in the server to accept remote connctions"""
    def local_port(self,action,iface,port):
        if str(port).isdigit() and (1024 < int(port) < 36565):
            suffix=["local-port",port]
        else:
            logger.error("port number expected is false, 1194 is recommanded")
            raise LocalportError("[ERROR] port number expected is false, 1194 is recommanded")
        return self.openvpn_config(iface,action,suffix)
    
    """specify the openvpn communication protocol"""
    def communication_protocol(self,action,iface,prot):
        if prot not in self.protocol:
            logger.error("%s can not be used as OpenVPN communication protocol! udp was set by default" %prot)
            raise ProtocolError("[ERROR] %s can not be used as OpenVPN communication protocol! udp was set by default" %prot)
        suffix=["protocol"]
        suffix.append(prot)
        return self.openvpn_config(iface,action,suffix)

    """this method allow the user to add openvpn options that 
    are not supported by the vyatta configuration yet"""
    def additional_options(self,action,iface,options):
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
