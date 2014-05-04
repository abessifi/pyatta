#!/usr/bin/env python
""" this method have to be added to utils module"""
from subprocess import check_output,CalledProcessError
import os

class PathError(Exception): pass
class AddressError(Exception): pass
class IpformatError(Exception): pass
class InterfaceError(Exception): pass
class ActionError(Exception): pass
class validation():

    @staticmethod
    def ipvalidation(ipaddr):
        addr_portions = ipaddr.split('.')
        if len(addr_portions) != 4:
            return False
        for portion in addr_portions:
            if not portion.isdigit():
                return False
            elem = int(portion)
            if elem < 0 or elem > 255:
                return False
        return True

    @staticmethod
    def ifacevalidation(iface):
        try:
            interfaces=check_output("ls /sys/class/net",shell=True)
        except CalledProcessError as e:
            print ("[Critical] problem with extracting interfaces ! execution fails with return code %s" % e.returncode)
            return False
        mounted_ifaces = interfaces.split('\n')
        del mounted_ifaces[-1]
        if iface not in mounted_ifaces:
            return False
        return True

    @staticmethod
    def pathvalidation(path):
        return os.path.exists(path)
       
    @staticmethod
    def addrvalidation(addr):
        try:
            addresses = check_output("/sbin/ifconfig |grep 'inet addr'|awk '{print $2}'|sed 's/addr://g'",shell=True)
        except CalledProcessError as e:
            print ("[Critical] problem with extracting configured interfaces ! execution fails with return code %s" % e.returncode)
            return False
        activeaddr=addresses.split('\n')
        del activeaddr[-1]
        if addr not in activeaddr:
            return False
        return True

    """check if a given interface already exist"""
    @staticmethod
    def testiface(iface):
        if not validation.ifacevalidation(iface):
            raise InterfaceError("[ERROR] invalid interface")
        return True

    """check if a given ip address is into a valid format"""
    @staticmethod
    def testip(ipaddr):
        if not validation.ipvalidation(ipaddr):
            raise IpformatError("[ERROR] invalid ip address")
        return True

    """verify if a given path is valid"""
    @staticmethod
    def testpath(abspath):
        if not validation.pathvalidation(abspath):
            raise PathError("[ERROR] check your input path file")
        return True

