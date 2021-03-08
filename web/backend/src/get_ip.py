#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2016-2021  Ben Zou <ben_zou@wistron.com>
# This file is part of Plumas project.

import sys
from isc_dhcp_leases import Lease, IscDhcpLeases
from backend.src.SSHCmd2 import ssh_cmd2

def get_ip(mac):
    leases = IscDhcpLeases('/var/lib/dhcpd/dhcpd.leases')
    leases = leases.get_current()
    l = leases.get(mac.lower())
    if l is None:
        return None
    else:
        return l.ip

def get_ip2(mac):
    a=ssh_cmd2("10.38.120.200","root","111111")
    a.connect()
    ip =""
    for i in a.execCmd("python3 /root/Infinity_MACSendBySelf/src/get_ip.py %s"%(mac)):
        ip = i 
        break
 
    if ip == "None":
        return None
    else:
        return ip      
    


if __name__ == '__main__':
    print(get_ip(sys.argv[1]))
