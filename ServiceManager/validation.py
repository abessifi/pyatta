#!/home/vyos/vyos-api/bin/python
""" this method have to be added to utils module"""
import subprocess
import os

class validation():
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

    def ifacevalidation(iface):
        mounted_ifaces=subprocess.check_output("ls /sys/class/net",shell=True)
        if iface not in mounted_ifaces:
            return False
        return True

    def pathvalidation(path):
        return os.path.exists(path)
       
    def addrvalidation(addr):
        addresses = subprocess.check_output("/sbin/ifconfig |grep 'inet addr'|awk '{print $2}'|sed 's/addr://g'",shell=True)
        if addr not in addresses:
            return False
        return True
