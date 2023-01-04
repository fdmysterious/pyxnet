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


############################
# Endpoint type enum
############################

class Endpoint_Kind(Enum):
    Virtual = "virtual",
    """Describes an endpoint in the virtual world"""

    Phy = "phy",
    """Describes a phy interface, linking the virtual and real world."""

    Real = "real",
    """Describes an endpoint in the real world"""


############################
# Endpoint base class
############################

class Endpoint:
    def __init__(self, name: str, kind: Endpoint_Kind, parent: PyxNetObject):
        self.name   = name
        self.kind   = kind
        self.parent = parent

        self.ifname = None # Attached interface name from Endpoint_Connection

    @property
    def path(self):
        return f"{self.parent.name}/{self.name}"

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
        self.misc_data = dict()

    def __hash__(self) -> int:
        return str.__hash__(f"{self.a.path}|{self.b.path}")


    # --------- Instanciation and interface names

    def instanciate(self):
        self.log("Instanciate connection: {self.a.path} <-> {self.b.path}")

        if   self.a.kind == Endpoint_Kind.Real:
            if   self.b.kind == Endpoint_Kind.Real:
                pass # Nothing to do
            elif self.b.kind == Endpoint_Kind.Virtual:
                raise RuntimeError("Cannot connect a real endpoint to a virtual one")
            elif self.b.kind == Endpoint_Kind.Phy:
                pass # Nohting to do


        elif self.a.kind == Endpoint_Kind.Virtual:
            if   self.b.kind == Endpoint_Kind.Real:
                raise RuntimeError("Cannot connect a virtual endpoint to a real one")
            elif self.b.kind == Endpoint_Kind.Virtual:
                # TODO VEth 
            elif self.b.kind == Endpoint_Kind.Phy:
                # TODO Direct link


        elif self.a.kind == Endpoint_Kind.Phy:
            if   self.b.kind == Endpoint_Kind.Real:
                pass # Nothing to do, outside of the computer
            elif self.b.kind == Endpoint_Kind.Virtual:
                pass # TODO Direct link
            elif self.b.kind == Endpoint_Kind.Phy:
                pass # TODO Pipe link

    
    def remove(self):
        pass # TODO 