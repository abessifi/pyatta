#!/usr/bin/env python

from flask import abort, request
from flask.ext.restful import Resource, reqparse
import os
import sys
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from servicemanager.dhcp_handler import dhcpHandler
from execformat.formator import showConfig
from base_setup import auth
from servicemanager.validation import validation as vld
show=showConfig()
dhcp=dhcpHandler()

class dhcpMainServices(Resource):
    decorators=[auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dhcp_name', type = str,required = True,location = 'json')
        self.reqparse.add_argument('dhcp_subnet', type = str, required = True, location = 'json')
        self.reqparse.add_argument('range_start', type = str, required = True, location = 'json')
        self.reqparse.add_argument('range_stop', type = str, required = True, location = 'json')
        super(dhcpMainServices, self).__init__()

    def get(self):
        return show.formator(['dhcp-server'])

    def post(self):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if not dhcp.set_range_adresses(args['dhcp_name'],args['dhcp_subnet'],args['range_start'],args['range_stop']):
            return {'Error':'Operation failed when setting up basic config for %s! see logfile'%args['dhcp_name']}, 403
        return {'Info':'your basic dhcp setting has been set successfully under %s name'%args['dhcp_name']},200


class dhcpSuppServices(Resource):
    decorators=[auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dhcp_status', type = str, location = 'json')
        self.reqparse.add_argument('default_router', type = str, location = 'json')
        self.reqparse.add_argument('dns_server', type = str, location = 'json')
        super(dhcpSuppServices, self).__init__()

    def get(self,name):
        if not dhcp.check_dhcp_name(name):
            return {'Error':'%s: Provided dhcp Pool name does not exist!'%name}, 400
        if not request.json or not 'show_elem' in request.json:
            return {'Error':'request must include a list of keys that leads to a customized show!'}, 400
        show_elements=['dhcp-server','shared-network-name',name]
        show_elements.extend(request.json['show_elem'])
        output=show.formator(show_elements)
        if not output:
            return {'Error':'show operation failed! see logfile for more infos!'}, 400
        return output

    def optional_config_dhcp(self,action,name):
        if not dhcp.check_dhcp_name(name):
            return {'Error':'%s: Provided dhcp Pool name does not exist!'%name}, 400
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if not args and action=='delete':
            if not dhcp.dhcp_subnet('delete',name):
                return {'Error':'Deleting %s config failed! see logfile for more infos!'%name}, 403
            return {'Info':'config under %s was deleted successfully!'%name}, 200
        if 'dhcp_status' in args:
            if not dhcp.dhcp_status(action,name):
                return {'Error':'Setting new dhcp permission failed! see logfile!'}, 403
        if 'default_router' in args:
            if not dhcp.dhcp_dnsserver_default_router(action,'default_router',name,args['default_router']):
                return {'error':'Operation failed with default router manip'}, 403
        if 'dns_server' in args:
            if not dhcp.dhcp_dnsserver_default_router(action,'dns_server',name,args['dns_server']):
                return {'error':'Operation failed with dns server manip'}, 403
        if action == 'set':
            return {'Info':'Specified configs has been added to the current config successfully!'}, 201
        return {'Info':'Specified configs has been deleted from the current config successfully!'}, 200

    def put(self,name):
        return self.optional_config_dhcp('set',name)
    def delete(self,name):
        return self.optional_config_dhcp('delete',name)
