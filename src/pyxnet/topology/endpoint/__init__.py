"""
===============================
Definition of Topology endpoint
===============================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

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
# Endpoint connection tuple
############################

Endpoint_Connection = namedtuple("Endpoint_Connection", ["a","b"])


############################
# Endpoint base class
############################

class Endpoint:
    def __init__(self, name: str, kind: Endpoint_Kind, parent: PyxNetObject):
        self.name   = name
        self.kind   = kind
        self.parent = parent

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