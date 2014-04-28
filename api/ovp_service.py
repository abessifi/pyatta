#!/usr/bin/env python
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from servicemanager.ovp_handler import ovpHandler, CipherError, ProtocolError, FileError, ModeError, RoleError, LocalportError, InterfaceExist
from servicemanager.validation import AddressError, validation as vld
from base_setup import auth
from flask import abort, request
from flask.ext.restful import Resource, reqparse
from execformat.formator import showConfig

show=showConfig()
class ovpService(Resource):
    ovp = ovpHandler()
    decorators=[auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('interface', type = str,required = True,location = 'json')
        self.reqparse.add_argument('mode', type = str, required = True, location = 'json')
        self.reqparse.add_argument('local_vaddr', type = str , location = 'json')
        self.reqparse.add_argument('remote_vaddr', type = str, location = 'json')
        self.reqparse.add_argument('remote_host', type = str, location = 'json')
        self.reqparse.add_argument('push_vsubnet', type = str, location = 'json')
        self.reqparse.add_argument('sharedkey_gen', type = str, location = 'json')
        self.reqparse.add_argument('sharedkey_path', type = str, location = 'json')
        self.reqparse.add_argument('role', type = str, location = 'json')
        self.reqparse.add_argument('keyfiles_path', type = list, location = 'json')
        super(ovpService, self).__init__()

    def get(self):
        return show.formator(['interfaces','openvpn'])        

    def post(self):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        keys=args.keys()
        try:
            if not self.ovp.set_interface_vpn(args['interface']):
                return {'Warning':'setting %s failed! see log for more infos! '%args['interface']}, 403
            if not self.ovp.vpn_mode('set',args['interface'],args['mode']):
                return {'Error':'set mode %s:operation failed!'%args['mode']}, 403
        except InterfaceExist,e:
            return {'Error':'setting %s failed! see log file'%args['interface']}, 403
        except ModeError,m:
            return {'Error':'set mode %s failed!'%args['mode']}, 403
        if args['mode']=='site-to-site':
            if 'role' in keys:
                try:
                    if not self.ovp.tls_role('set',args['interface'],args['role']):
                        return {'error':'operation failed while setting role! see log file'}, 403
                except RoleError,m:
                    return {'Error':'set role %s failed! see logfile!'%args['role']},400
            if not set(['local_vaddr','remote_vaddr','remote_host']).issubset(set(keys)):
                return {'Bad Request':'request is missing required options [local_vaddr,remote_vaddr,remote_host] to be set'}, 400
            if not self.ovp.endpoint_local_remote_vaddr('set','local',args['interface'],args['local_vaddr']):
                return {'Bad request':'setting %s failed! checking log is recommanded!'%args['local_vaddr']},400
            if not self.ovp.endpoint_local_remote_vaddr('set','remote',args['interface'],args['remote_vaddr']):
                return {'Bad request':'setting %s failed! checking log is recommanded!'%args['remote_vaddr']},400
            if not self.ovp.define_local_remote_host('set',args['interface'],'remote',args['remote_host']):
                return {'Error':'setting %s failed! checking log is recommanded!'%args['remote_host']},400
        elif args['mode']=='server':
            if not 'push_vsubnet' in keys:
                return {'Bad Request':'request is missing required options to be set'}, 400
            if not self.ovp.server_range_addr('set',args['interface'],args['push_vsubnet']):
                return {'Error':'setting %s failed!'%args['push_vsubnet']},400
        if 'sharedkey_path' in keys:
            if 'sharedkey_gen' in keys:
                if not self.ovp.shared_keygen(args['sharedkey_gen']):
                    return{'warning':'generation pre shared secret failed! see logfile!'}, 403
            if not self.ovp.sharedkey_file_path('set',args['interface'],args['sharedkey_path']):
                return {'error':'setting pre shared secret failed! consulting logfile is recommanded!'},400
        if 'keyfiles_path' in args:
            if 'role' not in keys and args['mode']=='site-to-site':
                return {'Error':'in site-to-site mode you have to specify the endpoint role'}, 400
            
            for file in args['keyfiles_path']:
                try:
                    if not self.ovp.tls_files('set',args['interface'],file):
                        return {'Error':'setting file under %s failed! see logfile!'%file}, 403
                except FileError,e:
                    return {'Error':'operation failed when setting %s'%file}, 400
        else:
            return {'Error':'you have to specify at least tls conf or pre shared secret conf!'},400
        return {'Info':'your current openvpn setting have been set successfully under %s interface'%args['interface']},200


class ovpServiceOptions(Resource):
    decorators=[auth.login_required]
    ovp = ovpHandler()
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('local_host', type = str, location = 'json')
        self.reqparse.add_argument('route_vpn', type = str, location = 'json')
        self.reqparse.add_argument('encrypt_algo', type = str, location = 'json')
        self.reqparse.add_argument('local_port', type = int, location = 'json')
        self.reqparse.add_argument('communic_prot', type = str, location = 'json')
        self.reqparse.add_argument('additional_options', type = str, location = 'json')
        super(ovpServiceOptions, self).__init__()

    def get(self,interface):
        if not vld.testiface(interface):
            return {'Error':'%s does not exist!'%interface}, 400
        if not request.json or not 'show_elem' in request.json:
            return {'Error':'request must include a list of keys that leads to a customized show!'}, 400
        show_elements=['interfaces','openvpn',interface]
        show_elements.extend(request.json['show_elem'])
        output=show.formator(show_elements)
        if not output:
            return {'Error':'show operation failed! see logfile for more infos!'}, 400
        return output
    
    def optional_config_ovp(self,action,interface):
        args = dict((k,v) for k, v in self.reqparse.parse_args().iteritems() if v)
        if not args and action=='delete':
            if not self.ovp.del_vpn_config(interface):
                return {'Error':'Operation failed! see logfile for more infos!'},400
            return {'Info':'config under %s was deleted ssuccessfully!'%interface}, 200
        if 'local_host' in args:
            try:
                if not self.ovp.define_local_remote_host(action,interface,'local',args['local_host']):
                    return {'Error':'Sth wrong has been occured with %s, see logfile'%args['local_host']}, 403
            except AddressError,err:
                return {'Error':err.message}, 403
        if 'route_vpn' in args:
            if not self.ovp.access_route_vpn(action,interface,args['route_vpn']):
                return {'Error':'Sth wrong has been occured with static route, see logfile'}, 403
        if 'encrypt_algo' in args:
            try:
                if not self.ovp.encryption_algorithm(action,interface,args['encrypt_algo']):
                    return {'error':'Operation failed with %s as incryption algo! see logfile'%args['encrypt_algo']}, 403
            except CipherError,e:
                return {'Error':'%s: %s '%(args['encrypt_algo'],e.message)},403
        if 'local_port' in args:
            try:
                if not self.ovp.local_port(action,interface,args['local_port']):
                    return {'error':'Operation failed with %s as local port! see logfile'%args['local_port']}, 403
            except LocalportError,e:
                return {'Error':'%s:Invalid port!'%args['local_port']}, 403
        if 'communic_prot' in args:
            try:
                if not self.ovp.local_port(action,interface,args['communic_prot']):
                    return {'error':'Operation failed with %s as communication protocol! see logfile'%args['communic_prot']}, 403  
            except ProtocolError,e:
                return {'Error':'%s:Invalid communication protocol!'%args['communic_prot']}, 403
        if 'additional_options' in args:
            self.ovp.additional_options(self,action,interface,args['additional_options'])
        else:
            abort(400)
        if action == 'set':
            return {'Info':'Specified configs has been added to the current config successfully!'}, 201
        return {'Info':'Specified configs has been deleted from the current config successfully!'}, 201

    def put(self,interface):
        if not vld.testiface(interface):
            return {'Error':'%s does not exist!'%interface}, 400
        return self.optional_config_ovp('set',interface)

    def delete(self,interface):
        if not vld.testiface(interface):
            return {'Error':'%s does not exist!'%interface}, 400
        return self.optional_config_ovp('delete',interface)
