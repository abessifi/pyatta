#!/usr/bin/env python
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from flask.ext.restful import Resource
from base_setup import auth
from VyosSessionConfig import configsession
class session_handler(Resource):
    cs=configsession.ConfigSession()
    decorators=[auth.login_required]
    def get(self,action):
        if action=='setup':
            try:
                if not self.cs.session_exists():
                    self.cs.setup_config_session()
                    return {'Info':'config session is setup successfully!'}, 200
                else:
                    return {'warning':'session already exists'}, 400
            except SetupSessionFailed,ssf:
                return {'Error':ssf.message},400
        elif action=='teardown':
            if self.cs.session_exists():
                if self.cs.session_changed():
                    return {'warning':'changes have to be commited or discarded before closing session!'}, 400
                self.cs.teardown_config_session()
                return {'Info':'config session is closed up successfully'}, 200
            else:
                return {'warning':'there is not session that already exists'}, 400
        elif action=='commit':
            if not self.cs.session_changed():
                return {'warning':'there is no changes happened!'}, 400
            try:
                self.cs.commit()
                return {'Info':'changes have been commited successfully!'}, 200
            except OperationFailed,of:
                return {'Error':of.message}, 400
        elif action=='discard':
            if not self.cs.session_changed():
                return {'warning':'no new changes to discard!'}, 400
            try:
                self.cs.discard()
                return {'Info':'changes have been discarded successfully!'}, 200
            except OperationFailed,of:
                return {'Error':of.message}, 400

        elif action=='save':
            try:
                self.cs.save()
                return {'Info':'changes have been saved successfully!'}, 200
            except OperationFailed,of:
                return {'Error':of.message}, 400
        else:
            return {'Bad request':'Unknown requested path'}, 400
