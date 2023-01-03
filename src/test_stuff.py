from pyxnet.topology.objects           import PyxNetObject
from pyxnet.topology.objects.topology  import Topology
from pyxnet.topology.endpoint          import Endpoint, Endpoint_Kind

from pprint                            import pprint
from dataclasses                       import dataclass, asdict, field

from functools                         import partial

class MyTestObject(PyxNetObject):
    def __init__(self, name: str):
        super().__init__(name)

        # Init endpoints
        self.p0        = Endpoint("p0", Endpoint_Kind.Virtual, parent=self)
        self.p1        = Endpoint("p1", Endpoint_Kind.Virtual, parent=self)


if __name__ == "__main__":
    tt   = Topology()

    obj0 = tt.register(MyTestObject("obj0"))
    obj1 = tt.register(MyTestObject("obj1"))

    tt.connect(obj0.p0, obj1.p0)
    tt.connect(obj0.p1, obj1.p1)

    pprint(asdict(tt), indent=4)


