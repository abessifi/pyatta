#!/usr/bin/env python

import sys
import os
import logging
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from vyos_session import utils
from servicemanager.validation import validation as vld
from operations import configOpts
from execformat.formator import showConfig
from execformat.executor import session
from pprint import pprint

NSR = "nat source rule"
NDR = "nat destination rule"
logger = logging.getLogger(__name__)
utils.init_logger(logger)

class natHandler(configOpts):
    type=['source','destination']
    show=showConfig()

    def check_nat_rule_number(self,type,rule_num):
        if type not in self.type:
            logger.error("type %s is not valid!"%type)
            return False
        rules=self.show.formator(['nat'])[type]['rule'].keys()
        if rule_num not in rules:
            return False
        return True

    def nat_config(self,action,type,suffix):
        nat_params=[NSR]+suffix if type=='source' else [NDR]+suffix
        return self.set(nat_params) if action=='set' else self.delete(nat_params)

    def del_nat_rule(self,type,rule_num):
        return self.nat_config('delete',type,[rule_num])

    def nat_status(self,action,type,rule_num):
        status=[rule_num,"disable"]
        return self.nat_config(action,type,status)

    def nat_interfaces(self,action,type,rule_num,iface):
        if not vld.testiface(iface):
            logger.error("%s: no such interface name!"%iface)
            return False
        iface_orient = "inbound-interface" if type=="destination" else "outbound-interface"
        interface=[rule_num,iface_orient,iface]
        return self.nat_config(action,type,interface)

    def nat_filter_addr_port(self,action,type,rule_num,orient,addr_port):
        if not orient in self.type:
            logger.error("%s: invalid position!"%orient)
            return False
        if vld.testip(addr_port):
            suffix=[rule_num,orient,"address",addr_port+"/24"]
        elif str(addr_port).isdigit():
            suffix=[rule_num,orient,"port",addr_port]
        else:
            logger.error("%s: unknown type either it is an ip address or a port number in filtering operation!"%addr_port)
            return False
        return self.nat_config(action,type,suffix)

    def nat_translation_addr_port(self,action,type,rule_num,trans_addr_port):
        if vld.testip(trans_addr_port):
            suffix=[rule_num,"translation address",trans_addr_port]
        elif str(trans_addr_port).isdigit():
            suffix=[rule_num,"translation port",trans_addr_port]
        else:
            logger.error("%s: unknown type either it is an ip address or a port number in translation operation!"%addr_port)
            return False
        return self.nat_config(action,type,suffix)

    def nat_protocol(self,action,type,rule_num,prot="all"):
        suffix=[rule_num,"protocol",prot]
        return self.nat_config(action,type,suffix)

"""
session.setup_config_session()
obj=natHandler()
#obj.nat_interfaces('set','destination','444','inbound-interface','eth1')
#obj.nat_filter_addr_port('set','destination','444','source','192.168.2.0')
#obj.nat_filter_addr_port('delete','destination','444','source','80')
#obj.nat_protocol('delete','destination','444','tcp')
#obj.nat_translation_addr_port('delete','destination','444','8080')
#obj.nat_translation_addr_port('set','destination','444','10.0.0.1')
#obj.del_nat_rule('destination','444')
session.commit()
session.teardown_config_session()
"""
