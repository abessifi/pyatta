
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

class dns_handler(Resource):
    dns=DnsService.dnsservice()
    decorators = [auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('listen-on', type = str, location = 'json')
        self.reqparse.add_argument('name-server', type = str, location = 'json')
        self.reqparse.add_argument('cache-size', type = int , location = 'json')
        super(dns_handler, self).__init__()
    @staticmethod
    def dns_manager(action):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        for key in args.keys():
            if key=='listen-on':
                dns.listenon_interface(action,args[key])
            elif key=='name-server':
                dns.nameserver(action,args[key])
            elif key=='cache-size':
                dns.cache-size(action,args[key])
    def get(self):
        return(show.serviceoutput)
    def post(self):
        dns_manager('set')
    def delete(self):
        dns_manager('delete')

class dns_option_handler(Resource):
    options=['listen-on','name-server','cache-size']
    decorators = [auth.login_required]
    def get(self, option):
        dns_keys=['forwarding']
        if option in self.options:
            dns_keys.append(option)
            return show.customized_show(dns_keys)    
        else:
            abort(404)
