#!/usr/bin/env python
import os
import sys
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from operations import configOpts
from execformat.executor import session
from validation import validation as vld

PS = "protocols static"

class routingHandler(configOpts):
    def route(self,action,type,suffix):
        routing_params=[PS,type]
        if action=='set':
            routing_params.extend(suffix)
            return self.set(routing_params)
        routing_params.append(suffix)
        return self.delete(routing_params)

    def add_addr_route(self,dst_subnet,nexthop=""):
        if not vld.testip(dst_subnet):
            return False
        addr_params=[dst_subnet+"/24"]
        if nexthop=="":
            addr_params.append("blackhole distance 1")
        else:
            if not vld.addrvalidation(nexthop):
                return False
            addr_params.extend(["next-hop",nexthop])
        return self.route("set","route",addr_params)

    def delete_addr_route(self,dst_subnet):
        if not vld.testip(dst_subnet):
            return False
        return self.route("delete","route",dst_subnet+"/24")

    def set_interface_route(self,dst_subnet,next_iface):
        if not vld.testip(dst_subnet) or not vld.testiface(next_iface):
            return False
        interface_params=[dst_subnet+"/24","next-hop-interface",next_iface]
        return self.route("set","interface-route",interface_params)

    def delete_interface_route(self,dst_subnet):
        if not vld.testip(dst_subnet):
            return False
        return self.route("delete","interface-route",dst_subnet+"/24")


"""
session.setup_config_session()
obj = routingHandler()
obj.add_addr_route("192.168.2.0","192.168.2.1")
obj.set_interface_route("192.168.2.0","vtun0")
session.commit()
session.teardown_config_session()
"""
