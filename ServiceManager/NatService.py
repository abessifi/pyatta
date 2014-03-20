#!../bin/python

import sys
sys.path.append('/home/vyos/vyos-api/')
from ConfigOpt import config_opt
from ExecFormat import ExecutorFormator
NSR = "nat source rule"
NDR = "nat destination rule"

class snatservice(config_opt):
    execformat = ExecutorFormator()

    def disable_snat(self,rule_num,prefix=NSR):
        nat_params=[prefix,rule_num,"disable"]
        self.set(nat_params)		
	
    def enable_snat(self,rule_num,prefix=NSR):
        nat_params=[prefix,rule_num,"enable"]
        self.set(nat_params)

    def set_snat(self,prefix,suffix):
        nat_params=[prefix]
        nat_params.extend(suffix)
        self.set(nat_params)

    def del_snat(self,rule_num,prefix=NSR,suffix=""):
        nat_params=[prefix,rule_num,suffix]
        self.delete(nat_params)

    def del_snat_src_subnet(self,rule_num,prefix=NSR):
        self.del_snat(prefix,rule_num,"source address")

    def set_snat_outbound_interface(self,rule_num,outbound_iface,prefix=NSR,inout="outbound-interface"):
        suffix=[rule_num,inout,outbound_iface]
        self.set_snat(prefix,suffix)	

    def set_source_subnet(self,rule_num,src_adr):
        suffix=[rule_num,"source address",src_adr+"/24"]
        self.set_snat(NSR,suffix)

    def set_snat_translation_adr(self,rule_num,prefix=NSR,trans_adr="masquerade"):
        suffix=[rule_num,"translation address",trans_adr]
        self.set_snat(prefix,suffix)
        self.execformat.commit()

    def set_snat_protocol(self,rule_num,prefix=NSR,prot="all"):
        suffix=[rule_num,"protocol",prot]
        self.set_snat(prefix,suffix)
        self.execformat.commit()
		#self.execformat.save()
		
    def set_snat_src_port(self,rule_num,range_port_name_nbr,label_port="source port",prefix=NSR):
        suffix=[rule_num,label_port,range_port_name_nbr]
        self.set_snat(prefix,suffix)

class dnatservice(snatservice):
    execformat = ExecutorFormator()

    def disable_dnat(self,rule_num):
        self.disable_snat(rule_num,NDR)

    def enable_dnat(self,rule_num):
        self.enable_snat(rule_num,NDR)
	
    def del_dnat(self,rule_num,suffix=""):
        self.del_snat(rule_num,NDR,suffix)

    def del_dnat_dst_adr(self,rule_num):
        self.del_dnat(rule_num,"destination address")

    def set_dnat_inbound_interface(self,rule_num,inbound_iface):
        self.set_snat_outbound_interface(rule_num,inbound_iface,NDR,"inbound-interface")

    def set_dnat_dst_adr(self,rule_num,dst_adr):
        suffix=[rule_num,"destination address",dst_adr]
        self.set_snat(NDR,suffix)		

    def set_dnat_translation_adr(self,rule_num,trans_adr):
        self.set_snat_translation_adr(rule_num,NDR,trans_adr)		
        self.execformat.commit()
        self.execformat.save()

    def set_dnat_protocol(self,rule_num,prot):
        self.set_snat_protocol(rule_num,NDR,prot)		

    def set_dnat_dst_port(self,rule_num, range_port_name_nbr):
        self.set_snat_src_port(rule_num,range_port_name_nbr,"destination port",NDR)

    def set_dnat_trans_port(self):
        pass

obj = snatservice()
obj.set_snat_outbound_interface("123","eth0")
obj.set_source_subnet("123","192.168.5.0")
obj.set_snat_translation_adr("123")
#obj.set_snat_protocol("123")
#obj.set_snat_src_port("123","1234-3000")

"""
obj = dnatservice()
obj.set_dnat_inbound_interface("21","eth0")
obj.set_dnat_dst_adr("21","119.252.88.90")
obj.set_dnat_dst_port("21","2301")
obj.set_dnat_protocol("21","tcp")
obj.set_dnat_translation_adr("21","192.168.2.15") 
"""
