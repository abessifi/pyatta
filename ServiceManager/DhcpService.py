#!../bin/python

from ConfigOpt import config_opt

SDS = "service dhcp-server shared-network-name"

class dhcpservice(config_opt):

	def disable_dhcp(self,name):
		dhcp_params[SDS,name,"disable"]
		self.set(dhcp_params)
 	def enable_dhcp(self,name):
                dhcp_params[SDS,name,"enable"]
                self.set(dhcp_params)

	def del_dhcp_config(self,name,suffix=[]):
		dhcp_params=[SDS,name]
		dhcp_params.extend((suffix))
		self.delete(dhcp_params)

	def del_dhcp_default_router(self,name,subnet,defrouter):
		suffix=["subnet",subnet,"default-router",defrouter]
		self.del_dhcp_config(name,suffix)


	def del_dhcp_dns_server(self,name,subnet,dnsserver):
		suffix=["subnet",subnet,"dns-server",dnsserver]
                self.del_dhcp_config(name,suffix)
		
	def setup_dhcp_subnet(self,name,subnet,suffix=[]):
		dhcp_params=[SDS,name,"subnet",subnet+"/24"]
		dhcp_params.extend((suffix))
		self.set(dhcp_params)
	
	def setup_dhcp_default_router(self,name,subnet,defrouter):
		self.setup_dhcp_subnet(name,subnet,["default-router",defrouter])

	def setup_dhcp_dns_server(self,name,subnet,dnsserver):
                self.setup_dhcp_subnet(name,subnet,["dns-server",dnsserver])

	def set_range_adresses (self,name,subnet,adr_start,adr_stop):
		plage=["start",adr_start,"stop",adr_stop]
                self.setup_dhcp_subnet(name,subnet,plage)

