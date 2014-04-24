#!/usr/bin/env python
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from ServiceManager import OpenVPN
from base_setup import auth
from flask import abort
from flask.ext.restful import Resource, reqparse

class openvpn_handler(Resource):
    ov = OpenVPN.openvpn()
    decorators=[auth.login_required]
        
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('', type = str, location = 'json')
        self.reqparse.add_argument('name-server', type = str, location = 'json')
        self.reqparse.add_argument('cache-size', type = int , location = 'json')
        super(dns_handler, self).__init__()
