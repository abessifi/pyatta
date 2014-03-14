#!../bin/python

import sys
sys.path.append('../')
from ConfigOpt import config_opt

SDF="service dns forwarding"

class dnsservice(config_opt):
	dns_params = []

	def add_listenon_interface(self,interface):
		self.dns_params.extend((SDF,"listen-on",interface))
		self.set(self.dns_params)

	def del_listenon_interface(self,interface):
		self.dns_params.extend((SDF,"listen-on",interface))
                self.delete(self.dns_params)

	def add_nameserver(self,nameserver):
		self.dns_params.extend((SDF,"name-server",nameserver))
                self.set(self.dns_params)

	def del_nameserver(self,nameserver):
		self.dns_params.extend((SDF,"name-server",nameserver))
                self.delete(self.dns_params)

				


obj = dnsservice()
obj.del_listenon_interface("eth0")
#obj.add_nameserver("1.1.1.1")
