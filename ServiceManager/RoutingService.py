#!../bin/python

from ConfigOpt import config_opt
PS = "protocols static"

class routingservice(config_opt):
    def add_route(self,suffix):
        routing_params=[PS]
        routing_params.extend(suffix)
        self.set(routing_params)

    def delete_route(self,type,suffix):
        del_params=[PS,type,suffix]
        self.delete(del_params)
        
    def add_addr_route(self,dst_subnet,nexthop=""):
        addr_params=["route",dst_subnet+"/24"]
        if nexthop=="":
            addr_params.append("blackhole distance 1")
        else:
            addr_params.extend(("next-hop",nexthop))
        self.add_route(addr_params)

    def delete_addr_route(self,dst_subnet):
        self.delete_route("route",dst_subnet+"/24")

    def set_interface_route(self,dst_subnet,next_iface):
        interface_params=["interface-route",dst_subnet+"/24","next-hop-interface",next_iface]
        self.add_route(interface_params)

    def delete_interface_route(self,dst_subnet):
        self.delete_route("interface-route",dst_subnet+"/24")
"""
obj = routingservice()
obj.delete_interface_route("192.168.1.0")
obj.exe.commit()
obj.exe.save()
"""
