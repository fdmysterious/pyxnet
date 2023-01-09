===========================
Pyxnet: SDN testing library
===========================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: December 2022

:Abstract: `pyxnet` is a python library targetted at network testing, especially for
           external, embedded devices.


Introduction
============

`pyxnet` is the contraction of `py` for python, `net` for network, and a `x` for the crossover. It is a simple
python library somehow like `mininet`_, but more targetted towards embedded devices testing. It makes extensive
use of the `iproute2` linux utility suite, and `openvswitch`_.

.. _`mininet`: http://mininet.org
.. _`openvswitch`: https://www.openvswitch.org/

This library allows to create virtual network topologies, for instance assign specific MAC or IP addresses,
and instanciate this topology on a linux host, or generate a diagram of this toplogy using `graphviz`.


Dependencies
============

This library depends on the following elements:

- Linux only
- `openvswitch`_ must be installed, and the following commands must be available:

  - `ovs-vsctl`
  - `ovs-dpctl`
  - `ovs-ofctl`

- iproute interface is made using the `pyroute2`_ library.

.. _`pyroute2`: https://pyroute2.org/

- `graphviz` allows graph generation


Defining a network topology
===========================

A network topology is defined using the following elements:

- Topology objects
- Links between objects' endpoints

**Still WIP, will be completed**


License
=======

MIT License

Copyright (c) 2023 Florian Dupeyron <florian.dupeyron@mugcat.fr>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.