#!/usr/bin/env python

import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from vyos_session import utils
from flask.views import MethodView
from flask.ext.restful import Api

from dns_service import dnsService, dnsOptionService
from base_setup import auth, app, token_gen, db
from session_service import sessionService
from user_handler import UserListAPI, UserAPI
from ovp_service import ovpService, ovpServiceOptions
from ifconfig_service import ethernetIfaces, ifconfigService
from routing_service import routingService, showRoutingElement

#initialization
app.config['SECRET_KEY'] = utils.get_config_params('api_auth','secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = utils.get_config_params('api_auth','db_uri')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

#extensions
api = Api(app)
#add resources
api.add_resource(sessionService,'/v1.0/session/<action>')
api.add_resource(dnsService, '/v1.0/services/dns/forwarding')
api.add_resource(token_gen,'/v1.0/token')
api.add_resource(dnsOptionService,'/v1.0/services/dns/forwarding/<option>')
api.add_resource(UserListAPI, '/v1.0/users')
api.add_resource(UserAPI, '/v1.0/users/<int:id>', endpoint = 'user')
api.add_resource(ovpService,'/v1.0/services/interfaces/openvpn')
api.add_resource(ovpServiceOptions,'/v1.0/services/interfaces/openvpn/<interface>')
api.add_resource(ethernetIfaces,'/v1.0/services/interfaces/ethernet')
api.add_resource(ifconfigService,'/v1.0/services/interfaces/ethernet/<interface>')
api.add_resource(routingService,'/v1.0/services/routing')
api.add_resource(showRoutingElement,'/v1.0/services/routing/<option>')

if __name__ == '__main__':
    if not os.path.exists('/var/lib/pyatta/db.sqlite'):
        db.create_all()
    app.run(debug = True)
