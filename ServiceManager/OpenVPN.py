#!../bin/python

import sys
sys.path.append('../')
from ExecFormat import ExecutorFormator
from ConfigOpt import config_opt

class site_to_site_vpn(config_opt):
    def shared_keygen():
        # run generate openvpn key <filename>
        pass
    
    def set_interface_vpn(self):
        pass

    def set_endpoint_src_vaddr(self):
        pass

    def set_vpn_mode(self):
        pass

    def set_endpoint_dst_vaddr(self):
        pass

    def define_remote_host(self):
        pass

    def sharedkey_file_path(self):
        pass

    def set_tls_role(self):
        pass
    
    def define_files():

    def define_ca_crt_file(self):
        pass

    def define_cert_file(self):
        pass

    def define_key_file(self):
        pass
    
    def define_crl_file(self):
        pass

    def define_dh_file(self):
        pass
