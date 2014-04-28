#!/usr/bin/env python

from flask import abort, jsonify
from flask.ext.restful import Resource, reqparse
import os
import sys
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from servicemanager import dns_handler
from execformat.formator import showConfig
from base_setup import auth

show=showConfig()

"""this class define the crud of dns service api"""
class dnsService(Resource):
    dns=dns_handler.dnsHandler()
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
        super(dnsService, self).__init__()

    def notif_msg(self,action,key):
            if action == 'set':
                return {'Error':'Some problems has been occured when setting %s element'%key}, 403
            return {'Error':'Some problems has been occured when deleting %s element'%key}, 40

    """this method handle setup and delete possible dns configs"""
    def dns_manager(self,action):
        #recover json provided from incoming request into a dict
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if action=='delete' and not args:
            self.dns.del_dns()
            return {'Info':'Existing dns configs has been deleted successfully!'}, 200
        keys = args.keys()
        print keys
        for key in keys:
            if key=='listen-on':
                operation=self.dns.listenon_interface(action,args[key])
                if not operation:
                    return self.notif_msg(action, 'listen-on')
            elif key=='name-server':
                operation=self.dns.name_server(action,args[key])
                if not operation:
                    return self.notif_msg(action, 'name-server')
            elif key=='cache-size':
                operation=self.dns.cache_size(action,str(args[key]))
                if not operation:
                    return self.notif_msg(action, 'cache-size')
            else:
                abort(400)
        if action == 'set':
            return {'Info':'Provided configs are added to the current one successfully!'}, 201
        return {'Info':'Mentioned configs has been deleted successfully!'}, 200

    """this method returns existant dns configs"""
    def get(self):
        return show.formator(['dns'])

    """this method allows the set of possible dns configs"""
    def post(self):
        return self.dns_manager('set')
            #return {'Error':'some problems appeared! set up failed!'}, 403
        #return {'Info':'dns config element was set up successfully!'}, 201
        
 
    """this method allows the delete of possible dns configs"""
    def delete(self):
        if not self.dns_manager('delete'):
            return{'Error':'some problems appeared! delete failed!'}, 403
        return {'Info':'dns config element was deleted successfully!'}, 200

"""this class allows specific gets of dns options"""
class dnsOptionService(Resource):
    options=['listen-on','name-server','cache-size']
    decorators = [auth.login_required]
    def get(self, option):
        dns_keys=['dns','forwarding']
        if option in self.options:
            dns_keys.append(option)
            #pass research keys to the hole dict to extract desired info
            return show.formator(dns_keys)    
        else:
            abort(404)
