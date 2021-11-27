""" Contains base station builder functionality.
"""
from edge_sim_py.components.base_station import BaseStation
from edge_sim_py.component_builders.basic_builder import BasicBuilder


class BaseStationBuilder(BasicBuilder):
    """Class responsible for building base station objects."""

    def __init__(self) -> object:
        """Creates a builder responsible for creating base station objects.
        Returns:
            object: Created BaseStationBuilder object.
        """
        BasicBuilder.__init__(self)

    def create_objects(self, n_objects: int) -> list:
        """Creates a list of BaseStation objects.
        Args:
            n_objects (int): Number of BaseStation objects to create.
        Returns:
            list: Created BaseStation objects.
        """
        self.objects = [BaseStation(obj_id=i + 1) for i in range(n_objects)]
        return self.objects

    def set_coordinates_all_base_stations(self, coordinates: list) -> list:
        """Defines the coordinates for base station objects.
        Args:
            coordinates (list): Coordinates assigned to the base station objects.
        Returns:
            base_stations (list): Modified BaseStation objects.
        """
        for index, base_station in enumerate(self.objects):
            base_station.coordinates = coordinates[index]

        return self.objects

    def set_wireless_delay_all_base_stations(self, wireless_delay_values: list) -> list:
        """Defines the wireless delay of base station objects.

        Args:
            wireless_delay_values (list): Wireless delay values assigned to the base station objects.

        Returns:
            base_stations (list): Modified BaseStation objects.
        """
        for index, base_station in enumerate(self.objects):
            base_station.wireless_delay = wireless_delay_values[index]

        return self.objects
