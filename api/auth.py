#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from pprint import pprint

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = '546f21a4eb62845c60fc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/lib/pyatta/db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    error_msg=""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    email = db.Column(db.String(30))
    superuser=db.Column(db.Boolean, nullable=False)
    
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def set_email(self,email=""):
        self.email=email

    def set_superuser(self,su):
        self.superuser=su

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

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

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.errorhandler(405)
def not_found(error):
        return make_response(jsonify( { 'error': 'Request method not allowed!' } ), 405)

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'unauthorized access!','reason':User.error_msg } ), 401)
    

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

def parse_json():
    user = request.json.get('username')
    pwd = request.json.get('password')
    email=request.json.get('email')
    su=request.json.get('superuser')
    return user,pwd,email,su

@app.route('/v1.0/users', methods=['POST','GET'])
def new_user():
    if request.method=='POST':
        username, password, email, superuser= parse_json()
        if username is None or password is None or superuser is None or superuser not in [0,1]:
            abort(400)    # missing arguments
        if User.query.filter_by(username=username).first() is not None:
            abort(400)    # existing user
        user = User(username=username)
        user.hash_password(password)
        user.set_email(email)
        user.set_superuser(superuser)
        db.session.add(user)
        db.session.commit()
        return (jsonify({'username': user.username}), 201,
                {'Location': url_for('get_user', id=user.id, _external=True)})
    elif request.method=='GET':
        list_users= User.query.all()
        for user in list_users:
            print user.username,user.email
        return jsonify({"done":"done"})
    else:
        abort(405)    

@app.route('/v1.0/users/<int:id>', methods=['GET','DELETE','PUT'])
def RUD_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    if request.method=='GET':
        return jsonify({'username': user.username,'email':user.email})
    elif request.method=='DELETE':
        delete_status=user.username+" has been deleted from the database!"
        db.session.delete(user)
        db.session.commit()
        return jsonify({'Info':delete_status})
    
    elif request.method=='PUT':
        if username is None or password is None or superuser is None or superuser not in [0,1]:
            abort(400)
        #for elem in request.json.keys():
         #   user.keys        
    
    else:
        abort(405)

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(60)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

if __name__ == '__main__':
    if not os.path.exists('/var/lib/pyatta/db.sqlite'):
        db.create_all()
    app.run(debug=True)

