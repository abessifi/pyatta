#!../bin/python

from ConfigOpt import config_opt

PSR = "protocols static route"
class routingservice(config_opt):

	def add_route(self,dst_subnet,nexthop=""):
		routing_params=[PSR,subnet+"/24"]
		if nexthop=="":
			routing_params.append("blackhole distance 1")
		else:
			routing_params.extend(("next-hop",nexthop))

		self.set(routing_params)

	def delete_route(self,dst_subnet):
		self.delete(dst_subnet+"/24")


