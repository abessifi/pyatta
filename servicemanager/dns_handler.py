#!/usr/bin/env python

import sys
import os
import logging
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from vyos_session import utils
from operations import configOpts
from validation import ActionError, validation as vld

SDF="service dns forwarding"
logger = logging.getLogger(__name__)
utils.init_logger(logger)

class dnsHandler(configOpts):

    def dns_config(self,action,suffix=[]):
        dns_params=[SDF]
        dns_params.extend(suffix)
        if action == "set":
            return self.set(dns_params)
        elif action == "delete":
            return self.delete(dns_params)
        else:
            logger.error('unknown action %s!'%action)
            raise ActionError('unknown action %s!'%action)

    def listenon_interface(self,action,interface):
        if not vld.testiface(interface):
            return False
        return self.dns_config(action,["listen-on",interface])
            
    def name_server(self,action,nameserver):
        if not vld.testip(nameserver):
            return False
        return self.dns_config(action,["name-server",nameserver])

    def cache_size(self,action,cache):
        if not str(cache).isdigit():
            logger.error("provided entry %s as cache size is note valid"%cache)
            return False
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
