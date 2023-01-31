"""
====================================
Example topology with "real" objects
====================================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023

This example illustrates how objects existing in the real world
can be described and represented on the output diagram. These example
also shows how real and virtual endpoint can be linked together using
phy objects.
"""

import logging

from pyxnet.topology.objects          import PyxNetObject
from pyxnet.topology.objects.topology import Topology
from pyxnet.topology.objects.phy      import Phy

from pyxnet.topology.endpoint         import Endpoint_Kind
from pyxnet.platform.cleanup          import cleanup_all

from pyxnet.diagram                   import helpers as dghelpers

class MyVirtualObj(PyxNetObject):
    """
    Example declaration of a virtual network object
    """

    def __init__(self, name: str):
        super().__init__(name)

        # Define custom endpoints
        self.ep0 = self._endpoint_register("ep0", Endpoint_Kind.Virtual)
        self.ep1 = self._endpoint_register("ep1", Endpoint_Kind.Virtual)

    def export_graphviz(self, dot):
        return dghelpers.box_logo_node(dot, self.name, dghelpers.asset("icons/material/join_left.png"), f"Virtual: {self.name}")

    def instanciate(self):
        pass

class MyRealObj(PyxNetObject):
    """
    Example declaration of a real network object
    """

    def __init__(self, name: str):
        super().__init__(name)

        # Define custom endpoints
        self.ep0 = self._endpoint_register("ep0", Endpoint_Kind.Real)
        self.ep1 = self._endpoint_register("ep1", Endpoint_Kind.Real)

    def export_graphviz(self, dot):
        return dghelpers.box_logo_node(dot, self.name, dghelpers.asset("icons/material/join_right.png"), f"Real: {self.name}")

    def instanciate(self):
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # First, declare a topology object. This object will holds all objects declaration,
    # as well as links between these objects.
    tt = Topology(name="Topology with mixed objects")

    # Secondly, we declare the objects we will have in our topology.
    obj1 = tt.register(MyVirtualObj("obj1"))
    obj2 = tt.register(MyRealObj   ("obj2"))
    phy1 = tt.register(Phy         ("phy1"))
    phy2 = tt.register(Phy         ("phy2"))


    # Then, we connnect these objects together
    tt.connect(obj1.ep0, phy1.ep  ) # The "ep" endpoint of the phy object represents the virtual side
    tt.connect(obj1.ep1, phy2.ep  )
    tt.connect(obj2.ep0, phy1.rep ) # The "rep" endpoint of the phy object represents the real (hence the "r") side)
    tt.connect(obj2.ep1, phy2.rep )


    # Then, we can export our graph
    dot = tt.export_graphviz()
    dot.render("real_objects")
