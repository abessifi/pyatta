#!/usr/bin/env python

from flask import abort, request
from flask.ext.restful import Resource, reqparse
import os
import sys
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from servicemanager.routing_handler import routingHandler
from execformat.formator import showConfig
from base_setup import auth
from servicemanager.validation import validation as vld

show=showConfig()

class routingService(Resource):
    routing=routingHandler()
    decorators = [auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('route_subnet', type = str, location = 'json')
        self.reqparse.add_argument('nexthop', type = str, location = 'json')
        self.reqparse.add_argument('interface_route_subnet', type = str , location = 'json')
        self.reqparse.add_argument('nexthop_interface', type = str , location = 'json')
        super(routingService, self).__init__()

    def routing_manager(self,action):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if not args:
            abort(400)
        if 'route_subnet' in args:
            if action=='delete':
                if not self.routing.delete_addr_route(args['route_subnet']):
                    return {'error':'deleting static route subnet was failed! see logfile for more infos:'}, 403
            else:
                if 'nexthop' in args:
                    if not self.routing.add_addr_route(args['route_subnet'],args['nexthop']):
                        return {'error':'Setting static route was failed! see logfile for more infos:'}, 403
                if not self.routing.add_addr_route(args['route_subnet']):
                    return {'error':'Setting static route without nexthop was failed! see logfile for more infos:'}, 403
        if 'interface_route_subnet' in args:
            if action=='delete':
                if not self.routing.delete_interface_route(args['interface_route_subnet']):
                    return {'error':'deleting interface_route_subnet was failed! see logfile for more infos:'}, 403
            else:
                if not 'nexthop_interface' in args:
                    return {'Warning':'nexthop interface need to be mentioned in request body'}, 400
                if not self.routing.set_interface_route(args['interface_route_subnet'],args['nexthop_interface']):
                    return {'error':'Setting interface_route_subnet was failed! see logfile for more infos:'}, 403
        if action == 'set':
            return {'Info':'mentioned configs were set up on vyos successfully!'}, 201
        return {'Info':'mentioned configs were deleted on vyos successfully!'}, 200

    def get(self):
        return show.formator(['protocols','static'])
    def post(self):
        return self.routing_manager('set')
    def delete(self):
        return self.routing_manager('delete')

class showRoutingElement(Resource):
    decorators=[auth.login_required]
    options=['route','interface-route']

    def get(self, option):
        routing_keys=['protocols','static']
        if option not in self.options:
            abort (404)
        routing_keys.append(option)
        #pass research keys to the hole dict to extract desired info
        return show.formator(routing_keys)
