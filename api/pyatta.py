#!/usr/bin/env python

import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)

from base_setup import auth, app, token_gen, db, check_db_config, User
#from session_handler import session_handler
from user_handler import UserListAPI, UserAPI
from vyos_session import utils
from flask.views import MethodView
from flask.ext.restful import Api, marshal, fields
import logging

logger = logging.getLogger('pyatta')
utils.init_logger(logger)

user_fields = {
    'username':fields.String,
    'email':fields.String,
    'superuser':fields.Boolean,
}

## Create the API ##

api = Api(app)

# Add resources to API
#api.add_resource(session_handler,'/v1.0/session/<action>')
#api.add_resource(dns_handler, '/v1.0/service/dns/forwarding')
#api.add_resource(dns_option_handler,'/v1.0/service/dns/forwarding/<option>')
api.add_resource(token_gen,'/v1.0/token')
api.add_resource(UserListAPI, '/v1.0/users')
api.add_resource(UserAPI, '/v1.0/users/<int:id>', endpoint = 'user')

if __name__ == '__main__':
    
    if not check_db_config() :
        logger.error('No database detected. Please check the configuration file !') 
        sys.exit(1)
    
    db.create_all() # setup/connect database
    user = User(username='ahmed.bessifi', password='vaytess', email='ahmed.bessifi@home', superuser='0')
    db.session.add(user)
    db.session.commit()
    users = { 'users': map(lambda t: marshal(t, user_fields), User.query.all()) }
    logger.info(users)

    if app.debug:
        logger.info('Starting web server in debug mode..')
    else:
        logger.info('Starting web server..')

    app.run() # start flask app
    

