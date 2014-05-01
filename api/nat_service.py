#!/usr/bin/env python

from flask import abort, request
from flask.ext.restful import Resource, reqparse
import os
import sys
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from servicemanager.nat_handler import natHandler
from execformat.formator import showConfig
from base_setup import auth
from servicemanager.validation import validation as vld
show=showConfig()
nat=natHandler()
type = ['source','destination']

class natMainSetup(Resource):
    decorators=[auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('rule_num', type = int, required = True, location = 'json')
        self.reqparse.add_argument('nat_type', type = str, required = True, location = 'json')
        self.reqparse.add_argument('interface', type = str, required = True, location = 'json')
        self.reqparse.add_argument('translation_addr', type = str,required = True,location = 'json')
        self.reqparse.add_argument('orientation', type = str,required = True,location = 'json')
        self.reqparse.add_argument('addr_port', type = str,required = True,location = 'json')
        super(dhcpMainServices, self).__init__()

    def get(self):
        return show.formator(['nat'])

    def post(self):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if not args['nat_type'] in type or not args['orientation'] in type:
            return {'bad request':'nat_type and orientation requires valid value!'}, 400
        if not nat.check_nat_rule_number(args['nat_type'],args['rule_num']):
            return {'error':'%s already exists for %s type'%(args['rule_num'],args['nat_type'])}, 400
        if not nat.nat_interface('set',args['nat_type'],args['rule_num'],args['interface']):
            return {'error':'Operation failed when setting bound interface! see logfile!'}, 400
        if not nat.nat_filter_addr_port('set',args['nat_type'],args['rule_num'],args['orientation'],args['addr_port']):
            return {'error':'Operation failed when setting %s filter! see logfile'%args['orientation']}, 400
        if not nat.nat_translation_addr_port('set',args['nat_type'],args['rule_num'],args['translation_addr']):
            return {'error':'Operation failed with translation manip! see logfile for more infos!'}, 400
        return {'info':'mentioned nat basic configuration are set up successfully!'}, 201


class natSuppServices(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('protocol_filter', type = str, location = 'json')
        self.reqparse.add_argument('addr_port', type = int, location = 'json')
        self.reqparse.add_argument('orientation', type = str, location = 'json')
        self.reqparse.add_argument('translation_port', type = int, location = 'json')
        self.reqparse.add_argument('nat_status', type = str, location = 'json')
        super(dhcpMainServices, self).__init__()

    def get(self,type_rule_option):
        nat_type=type_rule_option.split('/')[0]
        nat_rule=type_rule_option.split('/')[1]
        if not nat_type in type:
            abort(404)
        if not nat.check_nat_rule_number(nat_type,nat_rule):
            return {'Error':'Provided nat rule number %s  under %s type does not exist!'%(nat_rule,nat_type)}, 400
        if not request.json or not 'show_elem' in request.json:
            return {'Error':'request must include a list of keys that leads to a customized show!'}, 400
        show_elements=['nat',nat_type,"rule",nat_rule]
        show_elements.extend(request.json['show_elem'])
        output=show.formator(show_elements)
        if not output:
            return {'Error':'show operation failed! see logfile for more infos!'}, 400
        return output

    def nat_manager(self,action,type_rule_option):
        nat_type=type_rule_option.split('/')[0]
        nat_rule=type_rule_option.split('/')[1]
        if not nat_type in type:
            abort(404)
        if not nat.check_nat_rule_number(nat_type,nat_rule):
            return {'Error':'Provided nat rule number %s  under %s type does not exist!'%(nat_rule,nat_type)}, 400
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if action == 'delete' and not args:
            if not nat.del_nat_rule(nat_type,nat_rule):
                return {'Error':'Deleting nat config under %s rule  %s failed! see logfile for more infos!'%(nat_type,nat_rule)}, 403
            return {'Info':'config under %s rule %s  was deleted successfully!'%(nat_type,nat_rule)}, 200
        if 'protocol_filter' in args:
            if not nat.nat_protocol(action,nat_type,nat_rule,args['protocol_filter']):
                return {'error':'Operation failed with protocol filter! see logfile'}, 403
        if 'addr_port' in args:
            if not 'orientation' in args:
                return {'warning':'orientation must be specified to set or delete address/port filter!'}, 400
            elif not args['orientation'] in type:
                return {'warning':'orientation can take only source/destination values!'}, 400
            if not nat.nat_filter_addr_port('set',nat_type,nat_rule,args['orientation'],args['addr_port']):
                return {'error':'Operation failed when setting %s filter! see logfile'%args['orientation']}, 400
        if 'translation_port' in args:
            if not nat.nat_translation_addr_port('set',nat_type,nat_rule,args['translation_port']):
                return {'error':'Operation failed with translation manip! see logfile for more infos!'}, 400
        if 'nat_status' in args:
            if not nat.nat_status(action,nat_type,nat_rule):
                return {'error':'Operation failed when specifying nat ability!'}, 403
        if action == 'set':
            return {'Info':'Specified configs has been added to the current config successfully!'}, 201
        return {'Info':'Specified configs has been deleted from the current config successfully!'}, 200

    def put(self,type_rule_option):
        return self.optional_config_dhcp('set',type_rule_option)
    def delete(self,type_rule_option):
        return self.optional_config_dhcp('delete',type_rule_option)
