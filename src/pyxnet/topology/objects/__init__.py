"""
===================================
Base definition of a network object
===================================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

import logging

from abc                      import ABC, abstractmethod
from dataclasses              import dataclass

from pyxnet.topology.endpoint import Endpoint, Endpoint_Kind


##################################
# Base network object class
##################################

class PyxNetObject(ABC):
    def __init__(self, name: str):
        super().__init__()
        self.name      = name
        self.log       = logging.getLogger(name)

        self.endpoints = set()

    def __hash__(self) -> int:
        return str.__hash__(self.name)

    def __iter__(self):
        yield from self.endpoints

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return repr(self.__dict__)

    def export_graphviz(self, dot):
        """
        Generate associated graphviz node representation for
        diagram export.

        :param dot: Object to export graph
        """

        dot.node(self.name, shape="box")


    # ---------------- Base operations for object

    @abstractmethod
    def instanciate(self):
        pass

    #@abstractmethod
    def remove(self):
        pass

    #@abstractmethod
    def up(self):
        pass

    #@abstractmethod
    def down(self):
        pass


    # ---------------- Endpoint registration

    def _endpoint_register(self, name: str, kind: Endpoint_Kind):
        endp = Endpoint(name, kind, parent=self)
        self.endpoints.add(endp)
        return endp