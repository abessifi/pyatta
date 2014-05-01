#!/usr/bin/env python
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from operations import configOpts

SW="service webproxy"
UF="url-filtering squidguard"
class webFilterHandler(configOpts):

    def webproxy_config(self,suffix):
        webproxy=[SW]
        webproxy.extend(suffix)
        self.set(webproxy)

    def set_webproxy_cache_size(self,size):
        webproxy_cache = ["mem-cache-size",size]
        self.webproxy_config(webproxy_cache)

    def set_listen_addr(self,addr):
        webproxy_addr=["listen-address",addr]
        self.webproxy_config(webproxy_addr)

    def set_block_category(self,category):
        block_cat=[UF,"block-category",category]
        self.webproxy_config(block_cat)

    def set_local_block(self,website):
        block_loc=[UF,"local-block",website]
        self.webproxy_config(block_loc)

    def set_default_action(self,action):
        if action in ["allow","block"]:
            default_action=[UF,"default-action",action]
            self.webproxy_config(default_action)

    def set_redirect_url(self,url):
        redirect_url=[UF,"redirect-url",url]
        self.webproxy_config(redirect_url)

"""
obj = webfiltering()
obj.set_listen_addr("192.168.2.1")
obj.set_local_block("facebook.com")
"""
