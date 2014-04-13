#!/usr/bin/env python

import sys
import os
from pprint import pprint
import os

topdir = os.path.dirname(os.path.realpath(__file__)) + "../../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)

from VyosParser.vyos_parser import decode_string, decode_string_to_json

import VyosParser


data_firewall = """
 firewall {
     all-ping enable
     broadcast-ping disable
     config-trap disable
     ipv6-receive-redirects disable
     ipv6-src-route disable
     ip-src-route disable
     log-martians enable
     name INvtun0 {
         default-action drop
         rule 1 {
             action accept
             icmp {
                 type-name echo-request
             }
             protocol icmp
         }
     }
     name OUTvtun0 {
         default-action drop
         rule 1 {
             action accept
             icmp {
                 type-name echo-reply
             }
             protocol icmp
         }
     }
     name inTLS {
         default-action drop
         rule 100 {
             action accept
             destination {
                 address 0.0.0.0
                 port 443
             }
             protocol tcp
             state {
                 new enable
             }
         }
     }
     name outTLS {
         default-action drop
         rule 101 {
             action accept
             state {
                 established enable
                 related enable
             }
         }
     }
     receive-redirects disable
     send-redirects enable
     source-validation disable
     syn-cookies enable
 }
"""
data_interfaces = """
 interfaces {
     ethernet eth0 {
         address dhcp
         duplex auto
         hw-id 08:00:27:6a:36:4c
         smp_affinity auto
         speed auto
     }
     ethernet eth1 {
         address 192.168.2.1/24
         duplex auto
         hw-id 08:00:27:c5:b1:f1
         smp_affinity auto
         speed auto
     }
     ethernet eth2 {
         duplex auto
         hw-id 08:00:27:62:f8:43
         smp_affinity auto
         speed auto
     }
     loopback lo {
     }
     openvpn vtun0 {
         local-port 1194
         mode server
         openvpn-option "--comp-lzo yes"
         protocol tcp-passive
         server {
             push-route 192.168.3.0/24
             subnet 10.1.1.0/24
         }
         tls {
             ca-cert-file /config/auth/ca.crt
             cert-file /config/auth/vyos-server.crt
             dh-file /config/auth/dh1024.pem
             key-file /config/auth/vyos-server.key
         }
     }
 }
"""
data_nat  ="""
nat {
     source {
         rule 123 {
             outbound-interface eth0
             source {
                 address 192.168.2.0/24
             }
             translation {
                 address masquerade
             }
         }
     }
 }
"""

data_protocols  ="""
 protocols {
     static {
     }
 }

"""

data_service ="""
 service {
     dhcp-server {
         disabled false
         shared-network-name Pool1 {
             authoritative disable
             subnet 192.168.2.0/24 {
                 default-router 192.168.2.1
                 dns-server 192.168.2.1
                 lease 86400
                 start 192.168.2.50 {
                     stop 192.168.2.150
                 }
             }
         }
     }
     dns {
         forwarding {
             cache-size 150
             listen-on eth0
             listen-on eth1
             listen-on eth2
             name-server 208.67.220.123
             name-server 208.67.222.123
         }
     }
     https {
         http-redirect enable
         listen-address 192.168.1.23
     }
     ssh {
         allow-root
         port 22
     }
 }
"""

data_system ="""
 system {
     config-management {
         commit-revisions 20
     }
     console {
     }
     host-name vyos
     login {
         user vyos {
             authentication {
                 encrypted-password $1$5HsQse2v$VQLh5eeEp4ZzGmCG/PRBA1
             }
             level admin
         }
     }
     ntp {
         server 0.pool.ntp.org {
         }
         server 1.pool.ntp.org {
         }
         server 2.pool.ntp.org {
         }
     }
     package {
         auto-sync 1
         repository community {
             components main
             distribution hydrogen
             password ""
             url http://packages.vyos.net/vyos
             username ""
         }
     }
     syslog {
         global {
             facility all {
                 level notice
             }
             facility protocols {
                 level debug
             }
         }
     }
     time-zone UTC
 }
"""

# data_dummy = """
# hello world {
# "hello world" hello world {
# 
# }
# }"""

data_many_keys = """
 ethernet eth0 {
     address dhcp
     description "This is a LAN interface"
     duplex auto
     hw-id 08:00:27:6a:36:4c
     smp_affinity auto
     speed auto
 }
 ethernet eth1 {
     address 192.168.2.1/24
     duplex auto
     hw-id 08:00:27:c5:b1:f1
     smp_affinity auto
     speed auto
 }
 ethernet eth2 {
     address 192.168.3.1/24
     duplex auto
     hw-id 08:00:27:62:f8:43
     smp_affinity auto
     speed auto
 }
"""

data_flat1 = """
     address 192.168.3.1/24
     duplex auto
     hw-id 08:00:27:62:f8:43
     smp_affinity auto
     speed auto

"""
data_flat2 = """
     auto-sync 1
     repository community {
         components main
         distribution hydrogen
         password ""
         url http://packages.vyos.net/vyos
         username ""
     }

"""

data_all = [data_many_keys, data_empty, data_firewall, data_interfaces, data_nat , data_protocols, data_service, data_system,data_flat1,data_flat2 ]  

## test it with some random data ##
if __name__ == '__main__':
    # from testdata import * # test data
    for _d in data_all:
        # pprint(decode_string(_d))
        print(decode_string_to_json(_d))



# vim: et sts=4:ts=4:sw=4
