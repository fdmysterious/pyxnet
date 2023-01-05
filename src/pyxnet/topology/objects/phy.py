"""
==========================================================
network interface as an object for representation purposes
==========================================================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

from pyxnet.diagram           import helpers as dghelp
from pyxnet.topology.objects  import PyxNetObject

from pyxnet.topology.endpoint import Endpoint, Endpoint_Kind

class Phy(PyxNetObject):
    def __init__(self, name: str, ifname: str = None):
        super().__init__(name)
        if not ifname:
            ifname = name

        self._ifname = ifname
        self.ep  = Endpoint(name=ifname, kind=Endpoint_Kind.Phy, parent=self)
        self.rep = Endpoint(name=f"{ifname}-real", kind=Endpoint_Kind.Real, parent=self)
        """This endpoint has no useful purpose, it is only for diagram representation"""

    @property
    def ifname(self):
        return self._ifname

    def export_graphviz(self, dot):
        dghelp.box_logo_node(dot, self.name, dghelp.asset("icons/nic-behind.png"), self.name)

    def instanciate(self):
        pass