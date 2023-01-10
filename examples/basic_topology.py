"""
=============================
Basic pyxnet topology example
=============================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023

This example illustrates basic usage of the pyxnet topology declaration and instanciation
"""

import logging

from pyxnet.topology.objects.topology import Topology
from pyxnet.topology.objects.switch   import Switch

from pyxnet.topology.endpoint         import Endpoint_Kind
from pyxnet.platform.cleanup          import cleanup_all

from pyxnet.diagram                   import helpers as dghelpers

class MyCustomSwitch(Switch):
    """
    This class illustrates how a custom network object can be created
    by simply inheriting base objects
    """

    def __init__(self, name: str, mac_addr: str = None, ip_addr: str = None):
        # Each topology object has a name
        super().__init__(name,
            mac_addr   = mac_addr, # Not mandatory
            ip_addr    = ip_addr,  # Not mandatory

            stp_config = {
                "rstp_enabled": True,     # Enable RSTP!
                "bridge_priority": 0x8000 # Set bridge priority
            }
        )

        # Init endpoints
        self.p0 = self._endpoint_register("p0", Endpoint_Kind.Virtual)
        self.p1 = self._endpoint_register("p1", Endpoint_Kind.Virtual)

        # Set endpoint RSTP properties
        self.p0.properties["stp_config"] = {
            "path_cost": 100,
            "priority":  0x8000,
        }

        self.p1.properties["stp_config"] = {
            "path_cost": 100,
            "priority": 0x8000,
        }


    def export_graphviz(self, dot):
        """
        Illustrate how it's possible to customize
        the diagram generated object
        """

        dghelpers.box_logo_node(dot, self.name, dghelpers.asset("icons/material/router.png"), f"Switch {self.name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # First, declare a topology object. This object will holds all objects declaration,
    # as well as links between these objects.
    tt = Topology(name="Basic topology")

    # Secondly, we declare the objects we will have in our topology.
    s1 = tt.register(MyCustomSwitch("s1", mac_addr="02:01:02:00:00:01", ip_addr="10.0.0.1/24"), group="group1")
    s2 = tt.register(MyCustomSwitch("s2", mac_addr="02:01:02:00:00:02", ip_addr="10.0.0.2/24"), group="group1")
    s3 = tt.register(MyCustomSwitch("s3", mac_addr="02:01:02:00:00:03", ip_addr="10.0.0.3/24"), group="group2")
    s4 = tt.register(MyCustomSwitch("s4", mac_addr="02:01:02:00:00:04", ip_addr="10.0.0.4/24"), group="group2")


    # Then, we connect these objects together
    tt.connect(s1.p0, s3.p0)
    tt.connect(s1.p1, s4.p0)
    tt.connect(s2.p0, s3.p1)
    tt.connect(s2.p1, s4.p1)

    # Then, we can export our graph
    dot = tt.export_graphviz()
    dot.render("output_graph")

    # Now, onto instanciation of our topology!
    cleanup_all()    # Precaution
    tt.instanciate() # Topology instanciation on host platform

    # Up objects
    s1.up()
    s2.up()
    s3.up()
    s4.up()

