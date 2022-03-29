"""This module contains network switches power consumption model."""


class SwitchPowerModel:
    """Network Switch Power Model based on switch's chassis and ports demand."""

    @classmethod
    def get_port_power_consumption(cls, device: object) -> float:
        """Gets the power consumption of a given switch's port based on its current bandwidth demand as by [1].

        [1] Reviriego, Pedro, et al. "Performance evaluation of energy
        efficient ethernet." IEEE Communications Letters 13.9 (2009): 697-699.

        Args:
            device (object): Switch port whose power consumption will be computed.

        Returns:
            power_consumption (float): Switch port's power consumption.
        """
        low_power = device["low_power_percentage"] * device["active_power"]
        load = device["bandwidth_demand"] / device["bandwidth"]

        power_consumption = low_power * (1 - load) + device["active_power"] * load

        return power_consumption

    @classmethod
    def get_power_consumption(cls, device: object) -> float:
        """Gets the power consumption of a network switch. Chassis equation is based on [1].

        [1] Conterato, Marcelo da Silva, et al. "Reducing energy consumption in SDN-based data center networks
        through flow consolidation strategies." Proceedings of the 34th ACM/SIGAPP Symposium on Applied Computing. 2019.

        Args:
            device (object): Network switch whose power consumption will be computed.

        Returns:
            power_consumption (float): Network switch's power consumption.
        """
        # Calculating the power consumption of switch ports
        ports_power_consumption = 0
        for link in device.simulator.first().topology.edges(data=True, nbunch=device):
            port = link[2]
            ports_power_consumption += cls.get_port_power_consumption(port)

        # Calculating the switch's power consumption
        power_consumption = device.chassis_power + ports_power_consumption

        return power_consumption
