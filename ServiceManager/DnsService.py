#!/usr/bin/env python

import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from ConfigOpt import config_opt
SDF="service dns forwarding"

class dnsservice(config_opt):

    def dns_config(self,action,suffix):
        dns_params=[SDF]
        dns_params.extend(suffix)
        if action == "set":
            self.set(dns_params)
        elif action == "delete":
            self.delete(dns_params)

    def add_listenon_interface(self,interface):
        self.dns_config("set",["listen-on",interface])

    def del_listenon_interface(self,interface):
        self.dns_config("delete",["listen-on",interface])

    def add_nameserver(self,nameserver):
        self.dns_config("set",["name-server",nameserver])

    def del_nameserver(self,nameserver):
        self.dns_config("delete",["name-server",nameserver])

"""
obj = dnsservice()
#obj.del_listenon_interface("eth2")
obj.del_nameserver("208.67.222.123")
#obj.add_listenon_interface("eth2")
#obj.add_listenon_interface("eth1")
#obj.add_nameserver("208.67.222.123")

"""
