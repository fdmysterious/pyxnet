"""
==============================
Tools to cleanup all the mess!
==============================
:Authors: - Théo Bourdon <theo.bourdon@elsys-design.com>
          - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: December 2022
"""

import logging

from pyxnet.platform.tools import ovs, ifp
from pyroute2              import NDB

__cleanup_log = logging.getLogger("cleanup")


def cleanup_dpctl():
    """
    Cleanup all pyxnet related openvswitch data paths
    """

    __cleanup_log.info("Cleanup datapaths...")

    ret = ovs.dpctl("dump-dps")
    switches = ret.stdout.decode("utf-8").strip().split("\n")

    deleted = 0
    for switch in switches :
        s = switch.split("@")
        if s != [""] and not s[1].startswith(ifp()):
            __cleanup_log.debug(f"Removing {s[1]} dp")
            ovs.dpctl("del-dp", s[1])
            deleted += 1
    __cleanup_log.info(f"> Deleted {deleted} dps")
    

def cleanup_vsctl():
    """
    Cleanup all pyxnet related openvswitch virtual switches
    """

    __cleanup_log.info("Cleanup virtual switches...")

    ret =  ovs.vsctl("list-br")
    bridges = ret.stdout.decode("utf-8").strip().split("\n")
    deleted = 0
    if bridges != [""]:
        for bridge in bridges :
            if bridge.startswith(ifp()):
                __cleanup_log.debug(f"Removing {bridge} virtual switch")
                ovs.vsctl("del-br", bridge)
                deleted += 1
    __cleanup_log.info(f"> Deleted {deleted} switches")

def cleanup_ports():
    """
    Cleanup all pyxnet related ip interfaces
    """

    __cleanup_log.info("Cleanup ip interfaces...")
    deleted = 0
    
    with NDB() as ndb:
        while True:
            veths = list(filter(lambda x: (x['kind'] == "veth") and (x["ifname"].startswith(ifp())), ndb.interfaces.dump()))
            
            if not veths:
                break
            else:
                veth = veths[0]
                __cleanup_log.debug(f"Removing {veth} interface")
                ndb.interfaces[veth].remove().commit()
                deleted += 1
      
    __cleanup_log.info(f"> Deleted {deleted} interfaces")
    

def cleanup_all():
    cleanup_dpctl()
    cleanup_vsctl()
    cleanup_ports()      
    
if __name__ == "__main__":
    cleanup_all()
