"""
===============================
Definition of Topology endpoint
===============================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

import logging

from collections import namedtuple
from dataclasses import dataclass, field
from abc         import ABC, abstractmethod

from enum        import Enum, auto

from pyroute2 import NDB

from pyxnet.platform.link    import (Link_Phy, Link_VEth, Link_Pipe)
from pyxnet.platform.tools   import ifp, sth


############################
# Endpoint type enum
############################

class Endpoint_Kind(Enum):
    Virtual = "virtual"
    """Describes an endpoint in the virtual world"""

    Phy = "phy"
    """Describes a phy interface, linking the virtual and real world."""

    Real = "real"
    """Describes an endpoint in the real world"""


############################
# Endpoint base class
############################

class Endpoint:
    def __init__(self, name: str, kind: Endpoint_Kind, parent: "PyxNetObject"):
        self.log        = logging.getLogger(f"Endpoint {name}")
        self.name       = name
        self.kind       = kind
        self.parent     = parent

        self._ifname    = None   # Attached interface name from Endpoint_Connection
        self.properties = dict() # Auxiliary properties

    @property
    def path(self):
        return f"{self.parent.name}/{self.name}"
    

    @property
    def ifname(self):
        if not self._ifname:
            raise RuntimeError(f"endpoint {self} has no associated interface")
        return self._ifname


    def __hash__(self) -> int:
        return str.__hash__(self.path)


    def __eq__(self, other):
        return self.path == other.path


    def __str__(self):
        return self.path


    def __repr__(self):
        return f"Endpoint(path={self.path}, kind={self.kind.value})"

    ####################

    def up(self):
        self.log.info("Up endpoint")

        if self.kind != Endpoint_Kind.Real:
            with NDB() as ndb:
                ndb.interfaces[self.ifname].set("state", "up").commit()
        else:
            self.log.warn("Real endpoint, assuming correct action on target")


    def down(self):
        self.log.info("Down endpoint")

        if self.kind != Endpoint_Kind.Real:
            with NDB() as ndb:
                ndb.interfaces[self.ifname].set("state", "down").commit()
        else:
            self.log.warn("Real endpoint, assuming correct action on target")


############################
# Endpoint connection tuple
############################

@dataclass
class Endpoint_Connection:
    a: Endpoint
    b: Endpoint

    def __post_init__(self):
        self.log       = logging.getLogger(f"{self.a.path} <-> {self.b.path}")
        self.link_obj  = None # Instanciated link object

    def __hash__(self) -> int:
        return str.__hash__(f"{self.a.path}|{self.b.path}")


    # --------- Instanciation and interface names

    def _instanciate_veth(self):
        self.a._ifname = ifp(f"{sth(self.a.parent.name)}-{sth(self.a.name)}")
        self.b._ifname = ifp(f"{sth(self.b.parent.name)}-{sth(self.b.name)}")

        # Look for MAC and IP address
        a_mac = self.a.properties.get("mac_addr", None)
        a_ip  = self.a.properties.get("ip_addr" , None)
        b_mac = self.b.properties.get("mac_addr", None)
        b_ip  = self.b.properties.get("ip_addr" , None)

        self.link_obj  = Link_VEth(
            self.a.ifname, self.b.ifname,
            p0_mac = a_mac, p1_mac = b_mac,
            p0_ip  = a_ip , p1_ip  = b_ip
        )

    def _instanciate_phy(self, ep_phy, ep_virtual):
        ep_virtual._ifname = ep_phy.name # Virtual EP is directly linked to phy
        ep_phy._ifname     = ep_phy.name

        # Take properties from virtual endpoint
        phy_mac            = ep_virtual.properties.get("mac_addr", None)
        phy_ip             = ep_virtual.properties.get("ip_addr" , None)

        self.link_obj      = Link_Phy(ep_phy.name, mac_addr=phy_mac, ip_addr=phy_ip)

    def _instanciate_pipe(self):
        self.a._ifname = self.b.name
        self.b._ifname = self.b.name
        pipe_name = ifp(f"{sth(self.a.name)}-{sth(self.b.name)}")
        self.link_obj = Link_Pipe(pipe_name, self.a.ifname, self.b.ifname)


    def instanciate(self):
        self.log.info(f"Instanciate connection: {self.a.path} <-> {self.b.path}")

        # Let's go to the if clause of death!!!!!!!!!!!!!!!!!!
        if   self.a.kind == Endpoint_Kind.Real:
            if   self.b.kind == Endpoint_Kind.Real:
                pass # Nothing to do
            elif self.b.kind == Endpoint_Kind.Virtual:
                raise RuntimeError("Cannot connect a real endpoint to a virtual one. There must be a Phy interface in-between.")
            elif self.b.kind == Endpoint_Kind.Phy:
                pass # Nohting to do
        elif self.a.kind == Endpoint_Kind.Virtual:
            if   self.b.kind == Endpoint_Kind.Real:
                raise RuntimeError("Cannot connect a virtual endpoint to a real one; There must be a Phy interface in-between.")
            elif self.b.kind == Endpoint_Kind.Virtual:
                self._instanciate_veth()
            elif self.b.kind == Endpoint_Kind.Phy:
                self._instanciate_phy(self.b, self.a)
        elif self.a.kind == Endpoint_Kind.Phy:
            if   self.b.kind == Endpoint_Kind.Real:
                pass # Nothing to do, outside of the computer
            elif self.b.kind == Endpoint_Kind.Virtual:
                self._instanciate_phy(self.a, self.b)
            elif self.b.kind == Endpoint_Kind.Phy:
                self._instanciate_pipe()

        if self.link_obj is not None:
            self.link_obj.instanciate()
        else:
            self.log.info("No virtual link instanciated")
            

    
    def remove(self):
        if self.link_obj is not None:
            self.link_obj.remove()
            self.link_obj = None # Go garbage collector... go!