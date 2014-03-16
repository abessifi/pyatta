#!../bin/python

import sys
sys.path.append('../')
from ConfigOpt import config_opt
from ExecFormat import ExecutorFormator
SDF="service dns forwarding"

class dnsservice(config_opt):
	exe = ExecutorFormator()

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
		self.exe.commit()

	def del_nameserver(self,nameserver):
		self.dns_config("delete",["name-server",nameserver])
		#self.exe.commit()
				


obj = dnsservice()
#obj.del_listenon_interface("eth0")
#obj.del_nameserver("208.67.222.123")
obj.add_listenon_interface("eth0")
#obj.add_listenon_interface("eth1")
obj.add_nameserver("208.67.222.123")

