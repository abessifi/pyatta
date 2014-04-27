#!/usr/bin/env python

import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from operations import configOpts
import validation as vld
SDF="service dns forwarding"

class dnsHandler(configOpts):

    def dns_config(self,action,suffix=[]):
        dns_params=[SDF]
        dns_params.extend(suffix)
        if action == "set":
            return self.set(dns_params)
        elif action == "delete":
            return self.delete(dns_params)
        else:
            raise vld.ActionError('unknown action %s!'%action)

    def listenon_interface(self,action,interface):
        return self.dns_config(action,["listen-on",interface])
            
    def name_server(self,action,nameserver):
        return self.dns_config(action,["name-server",nameserver])

    def cache_size(self,action,cache):
        return self.dns_config(action,["cache-size",cache])

    def del_dns(self):
        return self.dns_config("delete")

"""
obj = dnsservice()
#obj.del_listenon_interface("eth2")
obj.del_nameserver("208.67.222.123")
#obj.add_listenon_interface("eth2")
#obj.add_listenon_interface("eth1")
#obj.add_nameserver("208.67.222.123")

"""
