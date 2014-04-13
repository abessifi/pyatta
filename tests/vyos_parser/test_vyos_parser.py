
import pytest
import os
import sys
from pprint import pprint

topdir = os.path.dirname(os.path.realpath(__file__)) + "../../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)

from VyosParser.vyos_parser import decode_string, decode_string_to_json


single_header = "single_header"

def test_single_header():
    """ """
    h = decode_string(single_header)
    assert h != None
    assert len(h.keys()) == 1
    assert h["single_header"] == "on"

dble_header = "dble header"

def test_dble_header():
    """ """
    h = decode_string(dble_header)
    assert h != None
    assert len(h.keys()) == 1
    assert h["dble"] == "header"

empty_body1 = """ empty_body { 
}  """

def test_empty_body1():
    """ """
    h = decode_string(empty_body1)
    assert h != None
    assert len(h.keys()) == 1
    assert "empty_body" in h
    assert h["empty_body"] == {}

empty_body2 = """ empty body { 
}  """

def test_empty_body2():
    """ """
    h1 = decode_string(empty_body2)
    assert h1 != None
    assert len(h1.keys()) == 1
    assert "empty" in h1

    h2 = h1["empty"]
    assert h2 != None
    assert len(h2) == 1
    assert "body" in h2
    assert h2["body"] == {}

body1 =  """
             state {
                 active
             }
"""
def test_body1():
    h1 = decode_string(body1)
    assert h1
    assert len(h1) == 1
    assert "state" in h1
    
    h2 = h1["state"]
    assert h2 
    assert len(h2) == 1
    assert "active" in h2
    assert h2["active"] == "on"


body2 =  """
             state {
                 new enable
             }
"""

def test_body2():
    h1 = decode_string(body2)
    assert h1
    assert len(h1) == 1
    assert "state" in h1
    
    h2 = h1["state"]
    assert h2 
    assert len(h2) == 1
    assert "new" in h2
    assert h2["new"] == "enable"


body3 =  """
             rule {
                 destination {
                 }
             }
"""

def test_body3():
    h1 = decode_string(body3)
    assert h1
    assert len(h1) == 1
    assert "rule" in h1
    
    h2 = h1["rule"]
    assert h2 
    assert len(h2) == 1
    assert "destination" in h2
    assert h2["destination"] == {}

body4 =  """
             rule {
                 destination dhcp {
                 }
             }
"""

def test_body3():
    h1 = decode_string(body4)
    assert h1
    assert len(h1) == 1
    assert "rule" in h1
    
    h2 = h1["rule"]
    assert h2 
    assert len(h2) == 1
    assert "destination" in h2

    h3 = h2["destination"]
    assert h3
    assert len(h3) == 1
    assert "dhcp" in h3
    assert h3["dhcp"] == {}

# TODO: more that one unit (mix and match)

d1 = """
action 
default-action 
"--comp-lzo yes"
0.0.0.0
192.168.3.0/24
08:00:27:6a:36:4c
/config/auth/vyos-server.key
"""

def test_d1():
    h = decode_string(d1)
    assert h
    assert len(h) == 7
    assert "action" in h
    assert "default-action" in h
    assert '"--comp-lzo yes"' in h
    assert "0.0.0.0" in h
    assert "192.168.3.0/24" in h
    assert "08:00:27:6a:36:4c" in h
    assert "/config/auth/vyos-server.key" in h


d2 = """
action accept
default-action drop
openvpn-option "--comp-lzo yes"
address 0.0.0.0
push-route 192.168.3.0/24
hw-id 08:00:27:6a:36:4c
key-file /config/auth/vyos-server.key
"""

def test_d2():
    h = decode_string(d2)
    assert h
    assert len(h) == 7

    assert "action" in h
    assert h["action"] ==  "accept"

    assert "default-action" in h
    assert h[ "default-action" ] == "drop"

    assert "openvpn-option" in h
    assert h[ 'openvpn-option' ] ==  '"--comp-lzo yes"'

    assert "address" in h
    assert h[ "address" ] == "0.0.0.0"

    assert "push-route" in h
    assert h[ "push-route" ] == "192.168.3.0/24"

    assert "hw-id" in h
    assert h[ "hw-id" ] == "08:00:27:6a:36:4c"

    assert "key-file" in h
    assert h[ "key-file" ] == "/config/auth/vyos-server.key"

d3 = """
firewall {
}
interfaces {
}

nat {
}
protocols {
}
dhcp-server {
}

system {
}


"""

def test_d3():
    """docstring for test_d3"""
    h = decode_string(d3)
    assert h
    assert len(h) == 6
    keys = ["firewall", "interfaces", "nat", "protocols", "dhcp-server", "system"]
    for k in keys:
        assert k in h
        assert h[k] == {}
d4 = """
key-file /config/auth/vyos-server.key
action 
"--comp-lzo yes"
nat {
}
default-action 

protocols {
}
address 0.0.0.0
dhcp-server {
}
push-route 192.168.3.0/24
hw-id 08:00:27:6a:36:4c
"""


def test_d4():
    h = decode_string(d4)
    assert h
    assert len(h) == 10
    k1 = { "key-file": "/config/auth/vyos-server.key", "address": "0.0.0.0", "push-route": "192.168.3.0/24" }
    k2 = ["action", '"--comp-lzo yes"', "default-action"]
    k3 = ["nat", "protocols", "dhcp-server"]
    for k in k1:
        assert h[k] == k1[k]
    for k in k2:
        assert h[k] == "on"
    for k in k3:
        assert h[k] == {}

d5 = """
 ethernet eth0 {
     address dhcp
 }
 ethernet eth1 {
     address 192.168.2.1/24
 }
 ethernet eth2 {
     address 192.168.3.1/24
 }
"""

def test_d5():
    h = decode_string(d5)
    assert h
    assert len(h) == 1
    assert "ethernet" in h

    a = h["ethernet"]
    assert len(a) == 3
    assert "eth0" in a[0]
    assert "eth1" in a[1]
    assert "eth2" in a[2]
    
d6 = """
 listen-on eth0
 name-server 208.67.220.123
 listen-on eth1
 name-server 208.67.222.123
 listen-on eth2
"""

def test_d6():
    h = decode_string(d6)
    assert h
    assert len(h) == 2
    assert "listen-on" in h

    a1 = h["listen-on"]
    assert len(a1) == 3
    assert a1 == ["eth0", "eth1", "eth2"]

    a2 = h["name-server"]
    assert len(a2) == 2
    assert a2 == ["208.67.220.123", "208.67.222.123"]

# vim: et sts=4:ts=4:sw=4
