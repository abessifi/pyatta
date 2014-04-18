
#!/usr/bin/env python
from flask import abort, jsonify
from flask.ext.restful import Resource, reqparse
import os
import sys
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from ServiceManager import DnsService
from ExecFormat.showmodule import show_config
from base_setup import auth

show=show_config('dns')
"""this class define the crud of dns service api"""
class dns_handler(Resource):
    dns=DnsService.dnsservice()
    #all methods in this class can be invoked only for authenticated users
    decorators = [auth.login_required]
    """this constructor define the parser elements of 
    the json body in the incoming request"""
    def __init__(self):
        #only listen-on, name-server and cache-size elements will be filtered from the request body 
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('listen-on', type = str, location = 'json')
        self.reqparse.add_argument('name-server', type = str, location = 'json')
        self.reqparse.add_argument('cache-size', type = int , location = 'json')
        super(dns_handler, self).__init__()

    """this method handle setup and delete possible dns configs"""
    @staticmethod
    def dns_manager(action):
        #recover json provided from incoming request into a dict
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if action=='delete' and not args:
            self.dns.del_dns()
        for key in args.keys():
            if key=='listen-on':
                self.dns.listenon_interface(action,args[key])
            elif key=='name-server':
                self.dns.nameserver(action,args[key])
            elif key=='cache-size':
                self.dns.cache-size(action,args[key])

    """this method returns existant dns configs"""
    def get(self):
        return(show.serviceoutput)

    """this method allows the set of possible dns configs"""
    def post(self):
        dns_manager('set')

    """this method allows the delete of possible dns configs"""
    def delete(self):
        dns_manager('delete')

"""this class allows specific gets of dns options"""
class dns_option_handler(Resource):
    options=['listen-on','name-server','cache-size']
    decorators = [auth.login_required]
    def get(self, option):
        dns_keys=['forwarding']
        if option in self.options:
            dns_keys.append(option)
            #pass research keys to the hole dict to extract desired info
            return show.customized_show(dns_keys)    
        else:
            abort(404)
