"""
==========================
Virtual switch description
==========================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

from pyxnet.topology.objects  import PyxNetObject
from pyxnet.topology.endpoint import Endpoint, Endpoint_Kind

from pyxnet.platform.tools    import ovs, ifp, sth
from pyroute2                 import NDB

from dataclasses              import dataclass
from typing                   import Optional

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

@dataclass
class Switch_Endpoint_Config_STP:
    path_cost: int                   = 0
    priority: int                    = 0x8000
    num: Optional[int]               = None # None -> Not defined
    admin_edge: bool                 = True
    auto_edge: bool                  = False
    admin_port_state: Optional[bool] = False


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
            ovs.vsctl("set", "Bridge", self.ifname, f"other_config:rstp-address={self.mac_addr}")

        self.log.debug("-> Set IP Address?")
        if self.ip_addr is not None:
            self.log.info(f"Set bridge IP address to {self.ip_addr}")
            with NDB() as ndb:
                ndb.interfaces[self.ifname].add_ip(self.ip_addr).commit()

        self.log.debug("-> Set bridge STP/RSTP config")
        ovs.vsctl("set", "Bridge", self.ifname, f"stp_enable={_boolt[self.stp_config.stp_enabled]}")
        ovs.vsctl("set", "Bridge", self.ifname, f"rstp_enable={_boolt[self.stp_config.rstp_enabled]}")
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
        for p in self.endpoints:
            ovs.vsctl("add-port", self.ifname, p.ifname)

            # Configure RSTP properties
            if "stp_config" in p.properties:
                if isinstance(p.properties["stp_config"], Switch_Endpoint_Config_STP):
                    ep_stp_config = p.Properties["stp_config"]
                else:
                    ep_stp_config = Switch_Endpoint_Config_STP(**p.properties["stp_config"])

                # Mandatory properties
                ovs.vsctl("set", "Port", p.ifname, f"other_config:stp-path-cost={ep_stp_config.path_cost}")
                ovs.vsctl("set", "Port", p.ifname, f"other_config:rstp-path-cost={ep_stp_config.path_cost}")
                ovs.vsctl("set", "Port", p.ifname, f"other_config:rstp-port-priority={ep_stp_config.priority>>8}")
                ovs.vsctl("set", "Port", p.ifname, f"other_config:rstp-port-admin-edge={_boolt[ep_stp_config.admin_edge]}")
                ovs.vsctl("set", "Port", p.ifname, f"other_config:rstp-port-auto-edge={_boolt[ep_stp_config.auto_edge]}")
                
                # Optional properties
                if ep_stp_config.num is not None:
                    ovs.vsctl("set", "Port", p.ifname, f"other_config:rstp-port-num={ep_stp_config.num}")

                if ep_stp_config.admin_port_state is not None:
                    ovs.vsctl("set", "Port", p.ifname, f"other_config:admin_port_state={_boolt[ep_stp_config.admin_port_state]}")


    # ------------- Port managment

    def _endpoint_register(self, name: str, kind: Endpoint_Kind):
        # Check endpoint's kind
        if kind not in (Endpoint_Kind.Virtual, Endpoint_Kind.Phy):
            raise ValueError(f"Cannot register endpoint {endp} of kind {endp.kind} for virtual switch {self.name}")

        return super()._endpoint_register(name, kind)


    # ------------- Up/Down

    def up(self):
        # Up switch
        self.log.info("Up switch")

        with NDB() as ndb:
            ndb.interfaces[self.ifname].set("state", "up").commit()
        
        # Up ports
        for ep in self.endpoints:
            ep.up()

    def down(self):
        # Down switch
        self.log.info("Down switch")
        with NDB() as ndb:
            ndb.interfaces[self.ifname].set("state", "down").commit()

        # Down ports
        for ep in self.endpoints:
            ep.down()

    
    # ------------- Various properties

    @property
    def ifname(self):
        return ifp(sth(self.name))