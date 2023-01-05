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

from pyxnet.topology.objects import PyxNetObject
from pyxnet.platform.link    import (Link_Phy, Link_VEth, Link_Pipe)

from pyxnet.platform.tools   import ifp


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
    def __init__(self, name: str, kind: Endpoint_Kind, parent: PyxNetObject):
        self.name   = name
        self.kind   = kind
        self.parent = parent

        self._ifname = None # Attached interface name from Endpoint_Connection

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


############################
# Endpoint connection tuple
############################

@dataclass
class Endpoint_Connection:
    a: Endpoint
    b: Endpoint

    def __post_init__(self):
        self.log       = logging.getLogger("")
        self.link_obj  = None # Instanciated link object

    def __hash__(self) -> int:
        return str.__hash__(f"{self.a.path}|{self.b.path}")


    # --------- Instanciation and interface names

    def instanciate(self):
        self.log("Instanciate connection: {self.a.path} <-> {self.b.path}")
        # TODO # Manage IP addr and mac addresses for endpoints

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
                self.a.ifname = ifp(self.a.name)
                self.b.ifname = ifp(self.b.name)
                self.link_obj = Link_VEth(self.a.ifname, self.b.ifname)
            elif self.b.kind == Endpoint_Kind.Phy:
                self.a.ifname = self.b.name # endpoint A is directly linked to phy interface
                self.b.ifname = self.b.name
                self.link_obj = Link_Phy(self.b.name)
        elif self.a.kind == Endpoint_Kind.Phy:
            if   self.b.kind == Endpoint_Kind.Real:
                pass # Nothing to do, outside of the computer
            elif self.b.kind == Endpoint_Kind.Virtual:
                self.a.ifname = self.a.name
                self.b.ifname = self.a.name # endpoint B is linked directly to phy interface
                self.link_obj = Link_Phy(self.a.name)
            elif self.b.kind == Endpoint_Kind.Phy:
                self.a.ifname = self.b.name
                self.b.ifname = self.b.name
                pipe_name = ifp(f"pipe-{self.a.name}-{self.b.name}")
                self.link_obj = Link_Pipe(pipe_name, self.a.ifname, self.b.ifname)

        if self.link_obj is not None:
            self.link_obj.instanciate()
        else:
            raise RuntimeError("No link instanciated...")

    
    def remove(self):
        if self.link_obj is not None:
            self.link_obj.remove()
            self.link_obj = None # Go garbage collector... go!