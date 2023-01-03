"""
===================================
Base definition of a network object
===================================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

from abc         import ABC
from dataclasses import dataclass


##################################
# Base network object class
##################################

class PyxNetObject:
    def __init__(self, name: str):
        self.name = name

    def __hash__(self) -> int:
        return str.__hash__(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return repr(self.__dict__)