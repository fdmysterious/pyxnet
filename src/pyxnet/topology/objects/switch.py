"""
==========================
Virtual switch description
==========================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

from pyxnet.topology.objects  import PyxNetObject
from pyxnet.topology.endpoint import Endpoint, Endpoint_Kind

from pyxnet.platform.tools    import ovs, ifp
from pyroute2                 import NDB

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
        mac_addr: str = None,
        ip_addr: str  = None,

        stp_config: Switch_Config_STP = None
    ):
        super().__init__(name)

        # Parse STP config
        stp_config      = stp_config or Switch_Config_STP()
        if isinstance(stp_config, dict):
            stp_config = Switch_Config_STP(**stp_config)
        elif not isinstance(stp_config, Switch_Config_STP):
            raise TypeError(f"stp_config is not a Switch_Config_STP type")

        self.mac_addr   = mac_addr
        self.ip_addr    = ip_addr

        self.ports      = set()
        self.stp_config = stp_config


    # ------------- Instanciation

    def instanciate(self):
        _boolt = { True: "true", False: "false" }

        self.log.info("Instanciate virtual switch")

        self.log.debug("-> Create bridge")
        ovs.vsctl("add-br", self.ifname)

        self.log.debug("-> Set MAC address?")
        if self.mac_addr is not None:
            self.log.info(f"Set bridge MAC address to {self.mac_addr}")
            ovs.vsctl("set", "Bridge", self.name, f"other_config:rstp-address={self.mac_addr}")

        self.log.debug("-> Set IP Address?")
        if self.ip_addr is not None:
            self.log.info(f"Set bridge IP address to {self.ip_addr}")
            with NDB() as ndb:
                ndb.interfaces[self.ifname].add_ip(self.ip_addr).commit()

        self.log.debug("-> Set bridge STP/RSTP config")
        ovs.vsctl("set", "Bridge", self.ifname, f"stp_enabled={_boolt[self.stp_config.stp_enabled]}")
        ovs.vsctl("set", "Bridge", self.ifname, f"rstp_enabled={_boolt[self.stp_config.rstp_enabled]}")
        ovs.vsctl("set", "Bridge", self.ifname, f"other_config:stp-priority=0x{self.stp_config.bridge_priority:04X}")
        ovs.vsctl("set", "Bridge", self.ifname, f"other_config:stp-path-cost={self.stp_config.path_cost}")
        ovs.vsctl("set", "Bridge", self.ifname, f"other_config:rstp-priority={self.stp_config.bridge_priority>>4}")
        # > TODO Path cost is set per port
        ovs.vsctl("set", "Bridge", self.ifname, f"other_config:rstp-ageing-time={self.stp_config.ageing_time}")
        ovs.vsctl("set", "Bridge", self.ifname, f"other_config:rstp-max-age={self.stp_config.max_age}")
        ovs.vsctl("set", "Bridge", self.ifname, f"other_config:rstp-forward-delay={self.stp_config.forward_delay}")
        ovs.vsctl("set", "Bridge", self.ifname, f"other_config:rstp-transmit-hold-count={self.stp_config.transmit_hold_count}")

        # Add ports
        self.log.debug("-> Add ports to bridge")
        for p in self.ports:
            ovs.vsctl("add-port", self.name, p.ifname)


    # ------------- Port managment

    def _port_register(self, port: Endpoint):
        # Check endpoint's kind
        if port.kind not in (Endpoint_Kind.Virtual, Endpoint_Kind.Phy):
            raise ValueError(f"Cannot register endpoint {port} of kind {port.kind} for virtual switch {self.name}")

        self.ports.add(port)

    
    # ------------- Various properties

    @property
    def ifname(self):
        return ifp(self.name)