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


Defining a network topology
===========================

A network topology is defined using the following elements:

- Topology objects
- Links between objects
- Ports that attach a link end to an object.
