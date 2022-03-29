"""This module contains server's LinearPowerModel."""


class LinearPowerModel:
    """Power model description based on CloudSim's LinearPowerModel."""

    @classmethod
    def get_power_consumption(cls, device: object) -> float:
        """Gets the power consumption of a server.

        Args:
            device (object): Server whose power consumption will be computed.

        Returns:
            power_consumption (float): Server's power consumption.
        """
        static_power = device.static_power_percentage * device.max_power
        constant = (device.max_power - static_power) / 100
        utilization = device.demand / device.capacity

        power_consumption = static_power + constant * utilization * 100

        return power_consumption
