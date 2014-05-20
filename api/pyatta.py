#!/usr/bin/env python

import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)

from base_setup import auth, app, TokenResource, db, check_db_config, User
#from session_handler import session_handler
from user_handler import UsersResource, UserResource
from vyos_session import utils
from flask.views import MethodView
from flask.ext.restful import Api, marshal, fields
import logging

logger = logging.getLogger('pyatta')
utils.init_logger(logger)

## Create the API ##

api = Api(app)

# Add resources to API
#api.add_resource(session_handler,'/v1.0/session/<action>')
#api.add_resource(dns_handler, '/v1.0/service/dns/forwarding')
#api.add_resource(dns_option_handler,'/v1.0/service/dns/forwarding/<option>')
api.add_resource(TokenResource,'/v1.0/token')
api.add_resource(UsersResource, '/v1.0/users')
api.add_resource(UserResource, '/v1.0/users/<int:id>', endpoint = 'user')


if __name__ == '__main__':
    
    if not check_db_config() :
        logger.error('No database detected. Please check the configuration file !') 
        sys.exit(1)
    
    if app.debug:
        logger.info('Starting web server in debug mode..')
    else:
        logger.info('Starting web server..')

    app.run(debug=True, host='0.0.0.0') # start flask app
    

