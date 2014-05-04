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

logger = logging.getLogger(__name__)
utils.init_logger(logger)
show=showConfig()
FWN = "firewall name"
ZPZ = "zone-policy zone"

class fwHandler(configOpts):
    orientation=['source','destination']
    actions=["drop","reject","accept"]
    states=["established","invalid","related"]	
    availability=["enable","disable"]

    def check_zone_name(self,zone):
        zone_names=show.formator(['zone-policy'])['zone'].keys()
        if zone not in zone_names:
            logger.error("%s may not match with any of the existing zone\'s name!"%zone)
            return False
        return True

    def check_firewall_name(self,firewall):
        fw_names=show.formator(['firewall'])['name'].keys()
        if firewall not in fw_names:
            logger.error("%s may not match with any of the existing firewall\'s name!"%firewall)
            return False
        return True

    def check_rule_from_fw_name(self,fw_name,rule):
        rules=show.formator(['firewall'])['name'][fw_name]['rule'].keys()
        if rule not in rules:
            logger.error("given rule number %s under firewall name %s is not valid!"%(rule,fw_name))
            return False
        return True

    def firewall_config(self,action,name,suffix=[]):
        if not suffix:
            firewall=[FWN,name]
        else:
            firewall=[FWN,name,"rule"]
            firewall.extend(suffix)
        if action=='set':
            return self.set(firewall)
        else:
            return self.delete(firewall)

    def default_action(self,action,name,reaction):
        if not reaction in self.actions:
            logger.error("%s: unexpected value for action!"%reaction)
            return False
        return self.firewall_config(action,name,['default-action',reaction])

    def zone_config(self,action,suffix):
        zone=[ZPZ]
        zone.extend(suffix)
        if action=='set':
            return self.set(zone)
        else:
            return self.delete(zone)

    def del_zone(self,zone_name):
        if not self.check_zone_name(zone_name):
            logger.error("mentioned zone %s to delete is not defined!"%zone_name)
            return False
        return self.delete([ZPZ,zone_name])
        
    def del_firewall(self,fw_name,rule_num=""):
        del_params=[FWN,fw_name]
        if rule_num:
            del_params.extend(['rule',rule_num])
        return self.delete(del_params)

    def zone_desc(self,action,zone_name,desc):
        description = [zone_name,"description",desc]
        return self.zone_config(action,description)

    def zone_interface(self,action,zone_name,iface):
        if not vld.testiface(iface):
            logger.error("the following interface %s does not exist!"%iface)
            return False
        interface = [zone_name,"interface",iface]
        return self.zone_config(action,interface)

    def setup_fw_on_zone(self,action,zone_dst,zone_src,firewall=""):
        if not self.check_zone_name(zone_src):
            logger.error("zone source does not exist!")
            return False
        if not self.check_firewall_name(firewall):
            logger.error("%s: mentioned firewall name does not exist!"%firewall)
            return False
        fw_on_zone=[zone_dst,"from",zone_src]
        if firewall:
            fw_on_zone.extend(["firewall name",firewall])		
        return self.zone_config(action,fw_on_zone)

    def rule_default_action(self,action,name,rule_num,reaction):
        if not reaction in self.actions:
            logger.error("%s: unexpected value for action!"%reaction)
            return False
        set_action=[rule_num,"action",reaction]
        return self.firewall_config(action,name,set_action)

    def rule_state(self,action,name,rule_num,state,allow):
        if not state in self.states:    #related,established,invalid
            logger.error("%s is not a valid value"%state)
            return False
        elif not  allow in self.availability:
            logger.error("%s: unknown such action! possible values: enable/disable!"%allow)
            return False
        set_state=[rule_num,"state",state,allow]
        return self.firewall_config(action,name,set_state)

    def protocol(self,action,name,rule_num,prot):
        protocol=[rule_num,"protocol",prot]
        return self.firewall_config(action,name,protocol)
			
    def src_dst_addr_port(self,action,name,rule_num,orient,addr="",portlist=[]):
        if not orient in self.orientation:
            logger.error("%s: invalid orientation! possible choices: source/destination"%orient)
            return False
        filter_params=[rule_num,orient]
        if addr and vld.testip(addr):
            filter_params.extend(['address',addr])
        elif portlist:
            for port in portlist:
                if not str(port).isdigit():
                    logger.error("%s: this is not a valid port number!"%port)
                    return False
            join_port=','.join(str(x) for x in portlist)
            filter_params.extend(['port',join_port])
        else:
            logger.error("non deterministic status!")
            return False
        return self.firewall_config(action,name,filter_params)

    def rule_ability(self,action,name,rule_num,status):
        if not status in self.availability:
            logger.error("%s not a valid state!"%status)
            return False
        rule_status=[rule_num,status]
        return self.firewall_config(name,action,rule_status)


"""
session.setup_config_session()
obj=fwHandler()
#obj.set_zone_desc('set','test_zone1','\"this is a zone set for testing fw_handler core\"')
#obj.set_zone_interface('set','test_zone1','eth2')
#obj.set_zone_interface('set','test_zone1','qdvsd')
#obj.default_action('set','test_firewall1','1234','accept')
#obj.default_action('set','test_firewall1','1234','blaaaaa')
#obj.rule_state('set','test_firewall1','1234','established','enable')
obj.protocol('set','test_firewall1','1234','tcp')
obj.src_dst_addr_port('set','test_firewall1','1234','destination',addr='192.168.2.1')
obj.src_dst_addr_port('set','test_firewall1','1234','source',portlist=[22,443,25,21])

session.commit()
#obj.setup_fw_on_zone(action,'mootez','test_zone1','blaa')
#obj.setup_fw_on_zone(action,'mootez','blaaaa','test_firewall1')
obj.setup_fw_on_zone('set','ahmed','mootez','outTLS')
#obj.setup_fw_on_zone('delete','mootez','test_zone1')
#obj.del_firewall('test_firewall1')
#print obj.check_firewall_name('test_firewall')
#print obj.check_firewall_name('test_firewallsv')
#obj.check_firewall_name('INvtun0')
#print obj.check_firewall_zone('mootez')
session.commit()
session.teardown_config_session()
"""
