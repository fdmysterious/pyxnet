"""
=================================
Global topology object definition
=================================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

from dataclasses import dataclass, field
from typing      import List, Tuple, Set, Dict

from pyxnet.topology.endpoint import Endpoint, Endpoint_Connection
from pyxnet.topology.objects  import PyxNetObject

import graphviz

@dataclass
class Topology:
    """
    Represents a network topology.
    A topology consists on a dict of network objects,
    and a set of endpoint connections.
    """

    name: str
    objects: Dict[str, PyxNetObject]= field(default_factory=dict)
    links: Set[Endpoint_Connection] = field(default_factory=set)


    # --------------- Endpoints managment

    def connect(self, endpA, endpB):
        """
        Adds a connection between endpoint A end endpoint B,
        only if the endpoints have no existing connection to anything.

        :param endpA: Endpoint A
        :param endpB: Endpoint B
        """

        # Check endpoint parents are in topology
        if endpA.parent.name not in self.objects:
            raise ValueError(f"{endpA} parent not registered in topology")
        if endpB.parent.name not in self.objects:
            raise ValueError(f"{endpB} parent not registered in topology")

        # Check endpoints are not already connected
        # FIXME: This O(n) check can lead to some bulky overhead when the topology become complex.
        # Is there any O(1) algo to do this?

        for x in self.links:
            if (x.a == endpA) or (x.b == endpB):
                raise ValueError(f"{endpA} is already connected")
            elif (x.a == endpB) or (x.b == endpB):
                raise ValueError(f"{endpB} is already connected")

        # Create endpoint connection
        self.links.add(Endpoint_Connection(endpA, endpB))
    

    def disconnect(self, endpA, endpB):
        """
        Try to disconnect endpoint A and endpoint B. If a connection
        was not existing between these two endpoints, nothing happens.

        :param endpA: Endpoint A
        :param endpB: Endpoint B
        """

        conn_a = Endpoint_Connection(endpA, endpB)
        conn_b = Endpoint_Connection(endpB, endpA)
        self.links.discard(conn_a)
        self.links.discard(conn_b)


    # --------------- Objects managmnet

    def register(self, obj: any):
        """
        Registers a network object in the topology

        :param obj: the object to register
        """

        if isinstance(obj, PyxNetObject):
            self.objects[obj.name] = obj
        else:
            raise TypeError(f"{obj} is not a pyxnet network object" )
        return obj


    def unregister(self, obj: any):
        """
        Unregister a network object from the topology

        :param obj: the object to unregister
        """

        if isinstance(obj, str):
            if obj in self.objects:
                del self.objects[obj]
        elif isinstance(obj, PyxNetObject):
            if obj.name in self.objects:
                del self.objects[obj]
        else:
            raise TypeError(f"{obj} is not a string nor a pyxnet network object")


    def get(self, name: str):
        self.objects[name]


    def __getitem__(self, name: str):
        return self.get(name)

    
    # --------------- Diagram export

    def export_graphviz(self):
        dot = graphviz.Graph(
            name=self.name,
            engine="circo",
            graph_attr={"fontname": "sans-serif"},
            edge_attr={"fontname": "sans-serif", "fontsize": "11"},
            node_attr={"fontname": "sans-serif"},
        )

        # Add nodes
        for key, node in self.objects.items():
            node.export_graphviz(dot)
        
        # Add edges
        for edge in self.links:
            dot.edge(edge.a.parent.name, edge.b.parent.name, headlabel=edge.b.name, taillabel=edge.a.name)

        return dot