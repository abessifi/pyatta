#!../bin/python

from ConfigOpt import config_opt

IE = "interfaces ethernet"

class  configinterface(config_opt):
	orient=["in","out","local"]

	def ethernet_config(self,suffix):
		iface_config=[IE]
		iface_config.extend(suffix)
		self.set(iface_config)
	
	def set_addr_interface(self,interface,addr,vlan_label="",vlan_id=''):
		address = [interface,vlan_label,vlan_id,"address",addr]
		self.ethernet_config(address)

	def set_hw_id(self,interface,hwid):
		hw= [interface,"hw-id",hwid]
		self.ethernet_config(hw)

	def set_iface_desc(self,interface,desc,vlan_label="",vlan_id=''):
		description = [interface,vlan_label,vlan_id,"description",desc]
		self.ethernet_config(description)

	def set_firewall_to_iface(self,interface,orient,fwname):
		if orient in self.orient:
			firewall = [interface,"firewall",orient,"name",fwname] 
			self.ethernet_config(firewall)

	def set_vlan_desc(self,interface,desc,vlan_id):
		self.set_iface_desc(interface,desc,"vif",vlan_id)

	def set_vlan_addr(self,interface,addr,vlan_id):			
		self.set_addr_interface(interface,addr,"vif",vlan_id)
