#!/home/vyos/vyos-api/bin/python
""" this method have to be added to utils module"""
import subprocess
import os

class PathError(Exception): pass
class AddressError(Exception): pass
class IpformatError(Exception): pass
class InterfaceError(Exception): pass

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
        interfaces=subprocess.check_output("ls /sys/class/net",shell=True)
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
        addresses = subprocess.check_output("/sbin/ifconfig |grep 'inet addr'|awk '{print $2}'|sed 's/addr://g'",shell=True)
        activeaddr=addresses.split('\n')
        del activeaddr[-1]
        if addr not in activeaddr:
            return False
        return True
