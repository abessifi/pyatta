#!/usr/bin/env python

from operations import configOpts

FWN = "firewall name"
ZPZ = "zone-policy zone"
class fwHandler(configOpts):
	actions=["drop","reject","accept","inspect"]
	state=["established","invalid","related"]	
	availability=["enable","disable"]

	def firewall_config(self,name,suffix):
		firewall=[FWN,name,"rule"]
		firewall.extend(suffix)
		self.set(firewall)

	def zone_config(self,suffix):
		zone=[ZPZ]
		zone.extend(suffix)
		self.set(zone)

	def set_zone_desc(self,zone_name,desc):
		description = [zone_name,"description",desc]
		self.zone_config(description)

	def set_zone_interface(self,zone_name,iface):
		interface = [zone_name,"interface",iface]
		self.zone_config(interface)

	def setup_fw_on_zone(self,zone_src,zone_dst,firewall):
		fw_on_zone=[zone_src,"from",zone_dst,"name",firewall]		
		self.zone_config(fw_on_zone)

	def set_default_action(self,name,rule_num,action):
		if action in self.actions:
			set_action[rule_num,"action",action]		
			self.firewall_config(name,set_action)
	
	def set_rule_state(self,name,rule_num,state,allow):
		if state in self.states and allow in self.availability:
			set_state[rule_num,"state",state,allow]
			self.firewall_config(name,set_state)

	def set_protocol(self,name,rule_num,prot):
		protocol=[rule_num,"protocol",prot]
		self.firewall_config(name,protocol)
			
	def set_dest_port(self,name,rule_num,portlist,orient="destination"):
		port=[rule_num,orient,"port",portlist]
		self.firewall_config(name,port)


	def set_dest_addr(self,name,rule_num,addr_subnet,orient="destination"):
		addr=[rule_num,orient,"address",addr_subnet]
		self.firewall_config(name,addr)

 	def set_src_port(self,name,rule_num,portlist):
		self.set_dest_port(name,rule_num,portlist,"source")

        def set_src_addr(self,name,rule_num,addr_subnet):
		self.set_dest_addr(name,rule_num,addr_subnet,"source")

	def rule_state(self,name,rule_num,status):
		if status in availability:
			rule_status=[rule_num,status]
			self.firewall_config(name,rule_status)
