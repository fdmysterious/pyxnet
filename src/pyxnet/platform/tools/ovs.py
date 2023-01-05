"""
==================================
Simple tools to access openvswitch
==================================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

import logging
import subprocess


from pyroute2 import NDB

#####################################
# Error for OVS commands
#####################################
class OVS_Error(Exception):
    def __init__(self, msg):
        super().__init__(msg)

#####################################
# ovs command wrappers
#####################################

__ovs_vsctl_log = logging.getLogger("ovs-vsctl")
__ovs_dpctl_log = logging.getLogger("ovs-dpctl")


def vsctl(*args):
    try:
        __ovs_vsctl_log.debug(f"Call with args: {args}")
        return subprocess.run(["ovs-vsctl", *args], capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise OVS_Error(f"Failed {exc.cmd} call: {exc.stderr.decode('utf-8')}")


def dpctl(*args):
    try:
        __ovs_dpctl_log.debug(f"Call with args: {args}")
        return subprocess.run(["ovs-dpctl", *args], capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise OVS_Error(f"Failed {exc.cmd} call: {exc.stderr.decode('utf-8')}")