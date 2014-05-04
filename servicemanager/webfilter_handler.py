#!/usr/bin/env python
import sys
import os
import logging
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from operations import configOpts
from vyos_session import utils
from servicemanager.validation import validation as vld
from execformat.formator import showConfig
from execformat.executor import session

logger = logging.getLogger(__name__)
utils.init_logger(logger)
show=showConfig()
SW="service webproxy"
UF="url-filtering squidguard"
options=['local-block','block-category','local-block-keyword','local-ok','redirect-url']

class webFilteringHandler(configOpts):

    def check_webproxy_group_name(self,group_name):
        groups=show.formator(['webproxy'])['url-filtering']['squidguard']['source-group'].keys()
        if group_name not in groups:
            logger.error("%s is not a vaalid group name"%group_name)
            return False
        return True

    def webproxy_config(self,action,suffix):
        webproxy_params=[SW]
        webproxy_params.extend(suffix)
        if action=='set':
            return self.set(webproxy_params)
        else:
            return self.delete(webproxy_params)

    def webproxy_listen_on_addr_port(self,action,addr='',port=""):
        if not addr and not port:
            logger.error("must provide at least one full parameter!")
            return False
        if addr and vld.testip(addr):
            listen_on_params=["listen-address",addr]
        elif port and str(port).isdigit():
            listen_on_params=["default-port",port]
        else:
            logger.error("invalid provided parameters in listen_on stuff")
            return False
        return self.webproxy_config(action,listen_on_params)

    def webproxy_block(self,action,block_option,element):
        if not block_option in options:
            logger.error("%s: invalid given block action option!"%block_option)
            return False
        block_params=[UF,block_option,element]
        return self.webproxy_config(action,block_params)

    def default_action(self,action,permission):
        if not permission in ["allow","block"]:
            logger.error()
            return False
        default_action=[UF,"default-action",permission]
        return self.webproxy_config(action,default_action)

    def source_group(self,action,name,address):
        if not vld.testip(address):
            logger.error("%s is not a valid address!"%address)
            return False
        group_params=[UF,'source-group',name,'address',address+'/24']
        return self.webproxy_config(action,group_params)

    def group_rules(self,action,rule_num,option,element):
        if not option in options+['source-group']:
            logger.error("%s: unknown option to handle with webproxy rule!"%option)
            return False
        if option =='source-group': 
            if not self.check_webproxy_group_name(element):
                logger.error("%s: provided source-group name does not exists!"%element)
                return False
        group_params=[UF,'rule',rule_num,option,element]
        return self.webproxy_config(action,group_params)


"""
session.setup_config_session()
obj=webFilteringHandler()
obj.default_action('set','block')
#obj.set_default_action('blofbvf')
obj.webproxy_listen_on_addr_port('set',addr='192.168.2.1')
obj.webproxy_listen_on_addr_port('set',port='1234')
obj.webproxy_block('set','local-block','facebook.com')
obj.webproxy_block('set','block-category','porn')
#obj.webproxy_block('block-catecfvgory','porn')
obj.source_group('set','group-testing','192.168.2.0')
#obj.group_rules('set','123','source-group','group-testing')
#obj.group_rules('set','123','local-block','youtube.com')
#obj.group_rules('set','123','block-category','malware')

session.commit()
session.save()
session.teardown_config_session()
"""
