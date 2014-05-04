#!/usr/bin/env python

from flask import abort, request
from flask.ext.restful import Resource, reqparse
import os
import sys
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from servicemanager.fw_handler import fwHandler
from execformat.formator import showConfig
from base_setup import auth
from servicemanager.validation import validation as vld
show=showConfig()
firewall=fwHandler()

class zoneMainSetup(Resource):
    decorators=[auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('zone_interface', type = str, required = True, location = 'json')
        self.reqparse.add_argument('zone_name', type = str, required = True, location = 'json')
        super(zoneMainSetup, self).__init__()

    def get(self):
        return show.formator(['zone-policy'])

    def post(self):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if not firewall.zone_interface('set',args['zone_name'],args['zone_interface']):
            return {'return':'setting interface %s failed'%args['zone_interface']}, 400
        return {'info':'mentioned firewall basic configuration are set up successfully!'}, 201

class zoneServices(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('firewall', type = str, location = 'json')
        self.reqparse.add_argument('zone_src', type = str, location = 'json')
        self.reqparse.add_argument('description', type = str, location = 'json')
        super(zoneService, self).__init__()

    def get (self,zone_name):
        if not firewall.check_zone_name(zone_name):
            return {'bad request':'%s does not exist!'},400
        return show.formator(['zone-policy'])['zone'][zone_name]

    def zone_manager(self,action,zone_name):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if not firewall.check_zone_name(zone_name):
            return {'bad request':'%s does not exist!'},400
        if not args and action=='delete':
            if not firewall.del_zone(zone_name):
                return {'error':'Something wrong happened when deleting zone %s'%zone_name}, 403
        if 'description' in args:
            if not firewall.zone_desc(action,zone_name,args['description']):
                return {'error':'Operation failed when adding description to zone name: %s'%args['zone_name']}, 403
        if 'zone_src' in args:
            if not 'firewall' in args:
                return {'error':'firewall element must be specified in the request body!'}, 400
            if not firewall.setup_fw_on_zone(action,zone_name,args['zone_src'],args['firewall']):
                return {'error':'some problems has been occured when handling firewall between zones!'}, 400
        if action == 'set':
            return {'Info':'Specified configs has been added to the current config successfully!'}, 201
        return {'Info':'Specified configs has been deleted from the current config successfully!'}, 200

    def put(self,zone_name):
        self.zone_manager('set',zone_name)
    def delete(self,zone_name):
        self.zone_manager('delete',zone_name)


class initFirewall(Resource):
    decorators=[auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('fw_name', type=str, required=True, location='json')
        self.reqparse.add_argument('rule_num', type=int, required=True, location='json')
        self.reqparse.add_argument('fw_reaction', type=str, location='json')
        self.reqparse.add_argument('rule_reaction', type=str, required=True, location='json')
        super(initFirewall, self).__init__()

    def get(self):
        return show.formator(['firewall'])

    def post(self):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if firewall.check_firewall_name(args['fw_name']) and firewall.check_rule_from_fw_name(args['fw_name'],args['rule_num']):
            return {'error':'Given firewall identifier already exists'}, 403
        if not firewall.rule_default_action('set',args['fw_name'],args['rule_num'],args['rule_reaction']):
            return {'error':'Operation failed when setting rule default action! see logfile!'}, 403
        if 'fw_reaction' in args:
            if not firewall.default_action('set',args['fw_name'],args['default_action']):
                return {'error':'Operation failed when setting firewall default action! see logfile!'}, 400
        return {'info':'Basic firewall configuration is set up successfully!'}, 201

class firewallServices(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('rule_num', type=int, required=True, location='json')
        self.reqparse.add_argument('rule_state', type=str, location='json')
        self.reqparse.add_argument('allow', type=str, location='json')
        self.reqparse.add_argument('protocol_filter', type=str, location='json')
        self.reqparse.add_argument('address_filter', type=str, location='json')
        self.reqparse.add_argument('port_filter', type=list, location='json')
        self.reqparse.add_argument('filter_type', type=str, location='json')
        self.reqparse.add_argument('rule_availability', type=str, location='json')
        super(firewallServices, self).__init__()

    def get(self,fw_name):
        return show.formator(['firewall'])['name'][fw_name]

    def firewall_manager(self,action,fw_name):
        if not firewall.check_rule_from_fw_name(fw_name,args['rule_num']):
            return {'error':'Given firewall rule number does not exist'}, 400
        if ('address_filter' in args or 'port_filter' in args) and 'filter_type' not in args:
            return {'warning':'filter type value must be defined'}, 400
        if 'rule_state' in args:
            if not 'allow' in args:
                return {'warning':'allow value must be defined'}, 400
            if not firewall.rule_state(action,fw_name,args['rule_num'],args['rule_state'],args['allow']):
                return {'error':'rule state operation failed! see logfile for more infos!'}, 403
        if 'rule_availability' in args:
            if not firewall.rule_ability(action,fw_name,args['rule_num'],args['rule_availability']):
                return {'error':'rule ability operation is failed!'}, 403
        if 'protocol_filter' in args:
            if not firewall.protocol(action,fw_name,args['rule_num'],args['protocol']):
                return {'error':'protocol filter option failed! see logfile for more infos!'}, 403
        if 'address_filter' in args:
            if not firewall.src_dst_addr_port(action,fw_name,args['rule_num'],args['filter_type'],addr=args['address_filter']):
                return {'error':'address filter option failed! see logfile for more infos!'}, 403
        if 'port_filter' in args:
            if not firewall.src_dst_addr_port(action,fw_name,args['rule_num'],args['filter_type'],portlist=args['port_filter']):
                return {'error':'port filter option failed! see logfile for more infos!'}, 403
        if action == 'set':
            return {'Info':'Specified configs has been added to the current config successfully!'}, 201
        return {'Info':'Specified configs has been deleted from the current config successfully!'}, 200

    def put(self,fw_name):
        return self.firewall_manager('set',fw_name)
    def delete(self,fw_name):
        return self.firewall_manager('delete',fw_name)
