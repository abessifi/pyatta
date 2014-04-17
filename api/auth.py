#!/usr/bin/env python

import os
import sys
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from VyosSessionConfig import utils, configsession
from ServiceManager import DnsService
from ExecFormat.showmodule import show_config
from flask import Flask, jsonify, abort, session, request, make_response, url_for,g
from flask.views import MethodView
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import update
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

#initialization
app = Flask(__name__, static_url_path = "")
app.config['SECRET_KEY'] = utils.get_config_params('api_auth','secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = utils.get_config_params('api_auth','db_uri')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

#extensions
api = Api(app)
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

#parser fields
user_fields = {
    'username':fields.String,
    'email':fields.String,
    'superuser':fields.Boolean,
    'uri':fields.Url('user')
}
#object services
dns=DnsService.dnsservice()
cs=configsession.ConfigSession()

class User(db.Model):
    error_msg=""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(64))
    email = db.Column(db.String(30))
    superuser=db.Column(db.Boolean, nullable=False)

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def set_email(self,email=""):
        self.email=email

    def set_superuser(self,su):
        self.superuser=su

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


class UserListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True, help='No username provided', location='json')
        self.reqparse.add_argument('password', type=str, required=True,help='No password provided', location='json')
        self.reqparse.add_argument('email', type=str, default="", location='json')
        self.reqparse.add_argument('superuser', type=int, required=True,help='No superuser privilege provided', location='json')
        super(UserListAPI, self).__init__()
        
    def get(self):
        return { 'users': map(lambda t: marshal(t, user_fields), User.query.all()) }

    def post(self):
        args = self.reqparse.parse_args()
        if User.query.filter_by(username=args['username']).first() is not None:
            return {'error':'username name already allocated!'}, 400
        user = User(username=args['username'])
        user.hash_password(args['password'])
        user.set_email(args['email'])
        user.set_superuser(args['superuser'])
        db.session.add(user)
        db.session.commit()
        return { 'user': marshal(user, user_fields) }, 201

class UserAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, location = 'json')
        self.reqparse.add_argument('password', type = str, location = 'json')
        self.reqparse.add_argument('email', type = str , location = 'json')
        super(UserAPI, self).__init__()

    def get(self, id):
        user = User.query.get(id)
        if not user:
            abort(404)
        return { 'user': marshal(user, user_fields) }

    def put(self, id):
        user = User.query.get(id)
        if not user:
            abort(404)
        args = self.reqparse.parse_args()
        if args['password']:
            args['password']=pwd_context.encrypt(args['password'])
        for cle in ['username','password','email']:
            if args[cle]:
                user=User.query.filter_by(id=id).update({cle:args[cle]})
        db.session.commit()
        #return {'done':'done'}, 200        
        return { 'user': marshal(user, user_fields) }

    def delete(self, id):
        user = User.query.get(id)
        if not user:
            abort(404)
        db.session.delete(user)
        db.session.commit()
        return { 'Info': 'mentioned user has been deleted successfully!'}


@app.route('/v1.0/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(60)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'unauthorized access!','reason':User.error_msg } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    if password=='unused':
        user = User.verify_auth_token(username_or_token)
        if not user:
            #return {'invalid token:':username_or_token}, 401
            User.error_msg="invalid token!"
            return False
        # try to authenticate with username/password
    else:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            #username_or_token+"/"+password
            #return {'invalid provided username/password:':'failed'}, 401
            User.error_msg="username/password error!"
            return False

    g.user = user
    return True
"""
class DnsApi(Resource):
    decorators = [auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('listen-on', type = str, location = 'json')
        self.reqparse.add_argument('name-server', type = str, location = 'json')
        self.reqparse.add_argument('cache-size', type = str , location = 'json')
        super(DnsApi, self).__init__()
    def get(self):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        print args
    def post(self):
        pass
    def delete(self):
        pass
"""
@app.route('/v1.0/session/<action>',methods=['GET'])
@auth.login_required
def ConfSession(action):
    if action=='setup':
        try:
            if not cs.session_exists():
                cs.setup_config_session()
                return jsonify({'setup':'done'})
            else:
                return jsonify({'warning':'session already exists'})
        except SetupSessionFailed,ssf:
            return ssf.message
        except SessionAlreadyExists,sae:
            return sae.message
    elif action=='teardown':
        if cs.session_exists():
            cs.teardown_config_session()
            return jsonify({'Info':'config session is closed up successfully'})
        else:
            return jsonify({'warning':'there is not session that already exists'})
    else:
        return jsonify({'Bad request':'Unknown requested path'})

#api.add_resource(DnsApi, '/v1.0/service/dns/forwarding')
api.add_resource(UserListAPI, '/v1.0/users')
api.add_resource(UserAPI, '/v1.0/users/<int:id>', endpoint = 'user')

if __name__ == '__main__':
    if not os.path.exists('/var/lib/pyatta/db.sqlite'):
        db.create_all()
    app.run(debug = True)
