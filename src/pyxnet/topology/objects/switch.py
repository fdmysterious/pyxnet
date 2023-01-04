"""
==========================
Virtual switch description
==========================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

from pyxnet.topology.objects  import PyxNetObject
from pyxnet.topology.endpoint import Endpoint, Endpoint_Kind

from dataclasses              import dataclass

##############################
# Switch RSTP/STP config class
##############################
@dataclass
class Switch_Config_STP:
    stp_enabled: bool    = False
    rstp_enabled: bool   = False

    # Parameters for STP/RSTP
    bridge_priority: int = 0x8000
    path_cost: int       = 0x0000

    # Parameters for RSTP only
    # > Parameters are copied from ovs-vsctl default values
    ageing_time          = 1000
    max_age              = 10
    forward_delay        = 15
    transmit_hold_count  = 7

    ## TODO # Per port config for RSTP
    # port_priority, port_num, path_cost, admin_edge, auto_edge, port_admin_state


class Switch(PyxNetObject):
    """
    Represents a virtual switch object
    """

    def __init__(self,
        name: str,
        stp_config: Switch_Config_STP = None
    ):
        super().__init__(name)

        # Parse STP config
        stp_config      = stp_config or Switch_Config_STP()
        if isinstance(stp_config, dict):
            stp_config = Switch_Config_STP(**stp_config)
        elif not isinstance(stp_config, Switch_Config_STP):
            raise TypeError(f"stp_config is not a Switch_Config_STP type")

        self.ports      = set()
        self.stp_config = stp_config


    # ------------- Instanciation

    def instanciate(self):
        # TODO #
        pass


    # ------------- Port managment

    def _port_register(self, port: Endpoint):
        # Check endpoint's kind
        if port.kind not in (Endpoint_Kind.Virtual, Endpoint_Kind.Phy):
            raise ValueError(f"Cannot register endpoint {port} of kind {port.kind} for virtual switch {self.name}")

        self.ports.add(port)