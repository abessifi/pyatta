#!/usr/bin/env python

from flask import abort, request
from flask.ext.restful import Resource, reqparse
import os
import sys
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from servicemanager.ifconfig import ifConfig
from execformat.formator import showConfig
from base_setup import auth
from servicemanager.validation import validation as vld
show=showConfig()

class ethernetIfaces(Resource):
    decorators = [auth.login_required]
    def get(self):
        return show.formator(['interfaces','ethernet'])

class ifconfigService(Resource):
    decorators = [auth.login_required]
    ifconfig=ifConfig() 
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('address', type = str, location = 'json')
        self.reqparse.add_argument('description', type = str, location = 'json')
        self.reqparse.add_argument('firewall', type = str, location = 'json')
        self.reqparse.add_argument('fw_orient', type = str, location = 'json')
        self.reqparse.add_argument('vlan_id', type = str, location = 'json')
        self.reqparse.add_argument('vlan_desc', type = str, location = 'json')
        self.reqparse.add_argument('vlan_addr', type = str, location = 'json')
        super(ifconfigService, self).__init__()

    def check_operation_status(self,operation):
        if not operation:
            return {'error':'Operation failed! see logfile for more infos:'}, 403
            
    def ifconfig_manager(self,action,interface):
        if not vld.testiface(interface):
            return {'Error':'%s does not exist!'%interface}, 400
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if 'address' in args:
            self.check_operation_status(self.ifconfig.addr_interface(action,interface,args['address']))
        if 'description' in args:
            self.ifconfig.addr_interface(action,interface,args['description'])
        if 'firewall' in args:
            if not 'fw_orient' in args:
                return {'Warning':'you have to specify, with firewall element, the appropriate orientation!'}, 400
            self.check_operation_status(self.ifconfig.firewall_to_iface(action,interface,args['fw_orient'],args['firewall']))
        if 'vlan_id' in args:
            if 'vlan_desc' in args:
                self.check_operation_status(self.ifconfig.vlan_desc(action,interface,args['vlan_desc'],args['vlan_id']))
            if 'vlan_addr' in args:
                self.check_operation_status(self.ifconfig.vlan_addr(action,interface,args['vlan_addr'],args['vlan_id']))
        else:
            abort(404)
        if action == 'set':
            return {'Info':'mentioned configs were set up on vyos successfully!'}, 201
        return {'Info':'mentioned configs were deleted on vyos successfully!'}, 200

    def get(self, interface):
        if not vld.testiface(interface):
            return {'Error':'%s does not exist!'%interface}, 400
        if not request.json or not 'show_elem' in request.json:
            return {'Error':'request must include a list of keys that leads to a customized show!'}, 400
        show_elements=['interfaces','ethernet',interface]
        show_elements.extend(request.json['show_elem'])
        output=show.formator(show_elements)
        if not output:
            return {'Error':'show operation failed! see logfile for more infos!'}, 400
        return output

    def put(self, interface):
        self.ifconfig_manager('set',interface)
    def delete(self, interface):
        self.ifconfig_manager('delete',interface)
