#!/usr/bin/env python
from flask import Flask,jsonify,make_response,g
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

app = Flask('auth')
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

"""this class provides the database schema even 
other methods needed for authentication"""
class User(db.Model):
    error_msg=""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(64))
    email = db.Column(db.String(30))
    superuser=db.Column(db.Boolean, nullable=False)

    """this method returns the hash of one password given as a parameter"""
    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    """this is a setter for email information"""
    def set_email(self,email=""):
        self.email=email

    """this is a setter for superuser status"""
    def set_superuser(self,su):
        self.superuser=su

    """this method checks if the password provided as input is valid"""
    def verify_password(self, password):
        return pwd_context.verify(password, self.password)
    
    """this method generates a temporary token needed for authentication"""
    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    """this method check if a given token still valid or not"""
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

"""this method handle error that returns with code 403 """
@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'unauthorized access!','reason':User.error_msg } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

"""this method is invoked when a request was sent and contains authentication elements"""
@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    if password=='unused':
        user = User.verify_auth_token(username_or_token)
        if not user:
            User.error_msg="invalid token!"
            return False
        # try to authenticate with username/password
    else:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            User.error_msg="username/password error!"
            return False

    g.user = user
    return True

"""this class allows temporary token generation"""
class token_gen(Resource):
    decorators = [auth.login_required]

    def get(self):
        #this token will be valid for 60 seconds
        token = g.user.generate_auth_token(60)    
        return {'token': token.decode('ascii'), 'duration': 60}, 201
