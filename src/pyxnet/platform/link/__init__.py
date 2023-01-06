"""
=======================
Virtual links managment
=======================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: November 2022
"""

import logging
from pyroute2 import NDB
from abc      import ABC, abstractmethod

from pyxnet.platform.tools import ovs

##########################################
# Base link class
##########################################

class Link(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def instanciate(self):
        pass

    @abstractmethod
    def remove(self):
        pass


##########################################
# Veth port managment
##########################################

class Link_VEth(Link):
    def __init__(self, p0_name, p1_name, p0_mac=None, p1_mac=None, p0_ip=None, p1_ip=None):
        super().__init__()

        self.log     = logging.getLogger(f"VEth {p0_name}@{p1_name}")

        self.p0_name = p0_name
        self.p1_name = p1_name

        self.p0_mac  = p0_mac
        self.p1_mac  = p1_mac

        self.p0_ip   = p0_ip
        self.p1_ip   = p1_ip

    def instanciate(self, create=True, exists_ok=True):
        self.log.info(f"Creating virtual eth ports {self.p0_name}@{self.p1_name}")

        with NDB() as ndb:
            if create:
                if not (self.p0_name in ndb.interfaces) or (self.p1_name in ndb.interfaces):
                    ndb.interfaces.create(ifname=self.p0_name, kind="veth", peer={"ifname": self.p1_name}).commit()
                elif not exists_ok:
                    raise RuntimeError(f"Interface {p0_name} or {p1_name} already exists")

            if self.p0_mac is not None:
                self.log.info(f"> Set {self.p0_name} MAC addr to {self.p0_mac}")
                ndb.interfaces[self.p0_name].set("address", self.p0_mac).commit()

            if self.p1_mac is not None:
                self.log.info(f"> Set {self.p1_name} MAC addr to {self.p1_mac}")
                ndb.interfaces[self.p1_name].set("address", self.p1_mac).commit()

            if self.p0_ip is not None:
                self.log.info(f"> Set {self.p0_name} IP addr to {self.p0_ip}")
                ndb.interfaces[self.p0_name].add_ip(self.p0_ip).commit()

            if self.p1_ip is not None:
                self.log.info(f"> Set {self.p1_name} IP addr to {self.p1_ip}")
                ndb.interfaces[self.p1_name].add_ip(self.p1_ip).commit()

        return self

    def remove(self):
        self.log.info(f"Remove virtual eth ports {self.p0_name}@{self.p1_name}")

        with NDB() as ndb:
            ndb.interfaces[self.p0_name].remove().commit()


##########################################
# Physical link managment
##########################################

class Link_Phy(Link):
    def __init__(self, name, mac_addr=None, ip_addr=None):
        super().__init__()

        self.log  = logging.getLogger(f"Phy {name}")
        self.name = name

        self.mac_addr = mac_addr
        self.ip_addr  = ip_addr

    def instanciate(self):
        self.log.info(f"Configure {self.name} physical link")
        if (self.mac_addr is not None):
            self.log.info(f"> Set {self.name} MAC addr to {self.mac_addr}")

            with NDB() as ndb:
                ndb.interfaces[self.name].set("state", "down").commit()
                ndb.interfaces[self.name].set("address", self.mac_addr).commit()
        
        if (self.ip_addr is not None):
            self.log.info(f"> Set {self.name} IP address to {self.ip_addr}")
            
            with NDB() as ndb:
                ndb.interfaces[self.name].add_ip(self.ip_addr).commit()

    
    def remove(self):
        pass


##########################################
# Pipe link managment
##########################################

class Link_Pipe(Link):
    """
    Bypass represents the following topology object:

        ┌───────┐
       0┼───────┼1
        └───────┘
         Pipe

        0 <=> 1

        This enables to bridge two links together transparently, for example
        to link to physical ports together.
    """

    def __init__(self, name, p0_name, p1_name, p0_mac=None, p1_mac=None, p0_ip=None, p1_ip=None):
        super().__init__()

        self.name           = name
        self.log            = logging.getLogger(f"Pipe {name}")

        self.p0_name        = p0_name
        self.p1_name        = p1_name

        self.p0_mac         = p0_mac
        self.p1_mac         = p1_mac

        self.p0_ip          = p0_ip
        self.p1_ip          = p1_ip

    ###########################

    def instanciate(self):
        self.log.info("Configure pipe")
        ovs.dpctl("add-dp", self.name)
        ovs.dpctl("add-if", self.name, self.p0_name)
        ovs.dpctl("add-if", self.name, self.p1_name)

        # Add rules
        self.log.debug("> Redirect 0 <=> 1")
        ovs.dpctl("add-flow", self.name, "in_port(1),eth()", "2")
        ovs.dpctl("add-flow", self.name, "in_port(2),eth()", "1")

        # Configure mac and IP addr
        if self.p0_mac is not None:
            self.log.debug(f"> Configure port0 mac to {self.p0_mac}")
            with NDB() as ndb:
                ndb.interfaces[self.p0_name].set("state", "down").commit()
                ndb.interfaces[self.p0_name].set("address", self.p0_mac).commit()
        if self.p1_mac is not None:
            self.log.debug(f"> Configure port1 mac to {self.p1_mac}")
            with NDB() as ndb:
                ndb.interfaces[self.p1_name].set("state", "down").commit()
                ndb.interfaces[self.p1_name].set("address", self.p1_mac).commit()
        if self.p0_ip is not None:
            self.log.debug(f"> Configure port0 IP to {self.p0_ip}")
            with NDB() as ndb:
                ndb.interfaces[self.p0_name].add_ip(self.p0_ip).commit()
        if self.p1_ip is not None:
            self.log.debug(f"> Configure port0 IP to {self.p1_ip}")
            with NDB() as ndb:
                ndb.interfaces[self.p1_name].add_ip(self.p1_ip).commit()

    def remove(self):
        self.log.info("Remove bypass")
        ovs.dpctl("del-dp", self.name)

    ###########################

    #def up(self):
    #    self.log.info("Up ports")

    #    with NDB() as ndb:
    #        ndb.interfaces[self.p0_name].set("state", "up").commit()
    #        ndb.interfaces[self.p1_name].set("state", "up").commit()

    #def down(self):
    #    self.log.info("Down ports")

    #    with NDB() as ndb:
    #        ndb.interfaces[self.p0_name].set("state", "down").commit()
    #        ndb.interfaces[self.p1_name].set("state", "down").commit()