#!../bin/python
"""this class implements the necessary fonctionnalities to setup 
an openvpn service in both site-to-site and server-client mode"""
import sys
sys.path.append('../')
from ExecFormat import ExecutorFormator
from ConfigOpt import config_opt
from RoutingService import routingservice
import validation as validate
from subprocess import check_output,CalledProcessError

class CipherError(Exception): pass
class LocalportError(Exception): pass
class ProtocolError(Exception): pass
class KeyfileError(Exception): pass
class ModeError(Exception): pass
class InterfaceExist(Exception): pass
IOV="interfaces openvpn"

class openvpn(config_opt):
    viface = "vtun"
    exe = ExecutorFormator()    
    RS = routingservice()
    algo_cipher=["des","3des","bf256","aes128","aes256"]
    protocol=["udp","tcp-passive","tcp-active"]
    keyfiles=["ca-cert","cert","dh","key"]
    role=["active","passive"]
    mode=["server","client","site-to-site"]
    vld = validate.validation()
    """check if a given interface already exist"""
    @staticmethod
    def testiface(iface_num):
        if not openvpn.vld.ifacevalidation(openvpn.viface+iface_num):
            raise validate.InterfaceError("[ERROR] invalid interface number")
        return True
    
    """check if a given ip address is into a valid format"""
    @staticmethod
    def testip(ipaddr):
        if not openvpn.vld.ipvalidation(ipaddr):
            raise validate.IpformatError("[ERROR] invalid ip address")
        return True

    """verify if a given path is valid"""
    @staticmethod
    def testpath(path):
        if not openvpn.vld.pathvalidation(abspath):
            raise validate.PathError("[ERROR] check your input path file")
        return True

    """this method allows for shared key generation used to establish site to site connection"""
    @staticmethod
    def shared_keygen(sharedkeyname):
        try:
            check_output("/usr/sbin/openvpn --genkey --secret /config/auth/"+sharedkeyname ,shell=True)
            return True
        except CalledProcessError as e:
            print ("[Critical] Sth wrong has been occurred ! execution fails with return code %s" % e.returncode)
            return False

    """this method have to restructure any command line and pass it to the executor"""
    def openvpn_config(self,iface_num,suffix=[]):
        openvpn_params=[IOV,self.viface+iface_num]
        openvpn_params.extend(suffix)
        self.set(openvpn_params)
        return " ".join(openvpn_params)

    """this method grant a new virtual interface for an 
    endpoint participant for openvpn connection"""
    def set_interface_vpn(self,iface_num):
        if openvpn.vld.ifacevalidation(openvpn.viface+iface_num):
            raise InterfaceExist("[WORNING] interface already exist")
        self.openvpn_config(iface_num)        
        return True

    """this method accord a local address for openvpn interface in site-to-site mode"""
    def set_endpoint_local_vaddr(self,iface_num,local_vaddr):
        if testiface(iface_num) and testip(local_vaddr):
            suffix=["local-address",local_vaddr]
            self.openvpn_config(iface_num,suffix)

    """this method allow openvpn endpoints to act on a specific mode"""
    def set_vpn_mode(self,iface_num,mode):
        if testiface(iface_num):
            if mode not in self.mode:
                raise ModeException("[ERROR] valid mode is required !")
            suffix=["mode",mode]
            self.openvpn_config(iface_num,suffix)

    """this method accord a local address for openvpn interface in site-to-site mode"""
    def set_endpoint_remote_vaddr(self,iface_num,remote_vaddr):
        if testiface(iface_num) and testip(remote_vaddr):
            suffix=["remote-address",remote_vaddr]
            self.openvpn_config(iface_num,suffix)

    """this method is used in both site-to-site and client-server mode,
        and let the passive endpoint to know the physical address of the active one"""
    def define_remote_host(self,iface_num,remote_host):
        if testiface(iface_num):
            if openvpn.vld.addrvalidation(remote_host):
                suffix=["remote-host",remote_host]
                self.openvpn_config(iface_num,suffix)
            else:
                raise validate.AddressError("No such address already configured!")

    """this method have to define the right path to reach shared 
    key file on a site-to-site connection"""
    def sharedkey_file_path(self,iface_num,path):
        if testiface(iface_num):
            if testpath(path):                
                suffix=["shared-secret-key-file",path]
                self.openvpn_config(iface_num,suffix)

    """this method create the static route to access the remote 
    subnet via the openvpn tunnel in a site-to-site mode"""
    def set_access_route_vpn(self,iface_num,dst_subnet):
        if testiface(iface_num) and testip(dst_subnet):
            self.RS.set_interface_route(dst_subnet,"vtun"+iface_num)

    """this method specify a specific role (passive,active) for an endpoint in tls mode"""
    def set_tls_role(self,iface_num,role):
        if testiface(iface_num):
            if role not in self.role:
                raise RoleError("[ERROR] unvalid role: possible choice:active, passive")
            suffix=["tls role",role]
            self.openvpn_config(iface_num,suffix)

    """this method specify the locations of all files used 
    to establish a vpn connection in client-server mode"""
    def define_files(self,iface_num,typefile,abspath):
        if testiface(iface_num):
            if typefile not in keyfiles:
                raise KeyfileError("[ERROR] unvalid keyfile type!")
            elif testpath(abspath):
                suffix=["tls",typefile+"-file",abspath]
                self.openvpn_config(iface_num,suffix)

    """this method has the ability to delete an openvpn 
    interface with its appropriate configuration """
    def del_vpn_iface(self,iface_num):
        if testiface(iface_num):
            openvpn_params=[IOV+iface_num]
            self.delete(openvpn_params)

    """in client-server mode, this method is able to 
    specify the subnet for the openvpn tunnel """
    def set_server_range_addr(self,iface_num,subnet):
        if testiface(iface_num) and testip(subnet):
            suffix=["server subnet",subnet+"/24"]
            self.openvpn_config(iface_num,suffix)

    """this method set a route on the server that will be pushed 
    to all clients during the connection establishment"""
    def push_root_subnet(self,iface_num,subnet):
        if testiface(iface_num) and testip(subnet):
            suffix=["server push-route",subnet+"/24"]
            self.openvpn_config(iface_num,suffix)

    """as far as the previous method,this on set a route on the server that 
    will be pushed to all clients during the connection establishment"""
    def push_root_nameserver(self,iface_num,nameserver):
        if testiface(iface_num) and testip(nameserver):
            suffix=["server name-server",nameserver]
            self.openvpn_config(iface_num,suffix)

    """setup the data encryption algorithm"""
    def set_encryption_algorithm(self,iface_num,alogrithm):
        if testiface(iface_num):
            suffix=["encryption"]
            if algorithm in self.algo_cipher:
                suffix.append(algorithm)
            else:
                raise CipherError("[ERROR] %s is not a valid ancryption algorithm! aes256 is set as default one" %algorithm)
            self.openvpn_config(iface_num,suffix)

    """define the local port number in the server to accept remote connctions"""
    def set_local_port(self,iface_num,port):
        if testiface(iface_num):
            suffix=["local-port"]
            if str(port).isdigit() and port < 36565:
                suffix.append(port)
            else:
                raise LocalportError("[ERROR] port number expected is false 1194 was set by default")
            self.openvpn_config(iface_num,suffix)

    """specify the openvpn communication protocol"""
    def communication_protocol(self,iface_num,prot):
        if testiface(iface_num):
            suffix=["protocol"]
            if prot in self.protocol:
                suffix.append(prot)
            else:
                raise ProtocolError("[ERROR] %s can not be used as OpenVPN communication protocol! udp was set by default" %prot)
            self.openvpn_config(iface_num,suffix)

    """this method allow the user to add openvpn options that 
    are not supported by the vyatta configuration yet"""
    def set_additional_options(self,iface_num,options):
        if testiface(iface_num):
            suffix = ["openvpn-option",options]
            self.openvpn_config(iface_num,suffix)


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
