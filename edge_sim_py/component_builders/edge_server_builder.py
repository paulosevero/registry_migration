""" Contains edge server builder functionality.
"""
from edge_sim_py.component_builders.basic_builder import BasicBuilder
from edge_sim_py.components.base_station import BaseStation
from edge_sim_py.components.edge_server import EdgeServer


class EdgeServerBuilder(BasicBuilder):
    """Class responsible for building edge server objects."""

    def __init__(self) -> object:
        """Creates a builder responsible for creating edge server objects.
        Returns:
            object: Created EdgeServerBuilder object.
        """
        BasicBuilder.__init__(self)

    def create_objects(self, n_objects: int) -> list:
        """Creates a list of EdgeServer objects.
        Args:
            n_objects (int): Number of EdgeServer objects to create.
        Returns:
            list: Created EdgeServer objects.
        """
        self.objects = [EdgeServer(obj_id=i + 1) for i in range(n_objects)]
        return self.objects

    def set_coordinates_all_edge_servers(self, coordinates: list) -> list:
        """Defines the coordinates for edge server objects.
        Args:
            coordinates (list): Coordinates assigned to the edge server objects.
        Returns:
            edge_servers (list): Modified EdgeServer objects.
        """
        for index, edge_server in enumerate(self.objects):
            edge_server.coordinates = coordinates[index]

            base_station = BaseStation.find_by(attribute_name="coordinates", attribute_value=edge_server.coordinates)
            edge_server.base_station = base_station
            base_station.edge_servers.append(base_station)

        return self.objects

    def set_capacity_all_edge_servers(self, capacity_values: list) -> list:
        """Defines the capacity for edge server objects.
        Args:
            capacity_values (list): Capacity values assigned to the edge server objects.
        Returns:
            edge_servers (list): Modified EdgeServer objects.
        """
        for index, edge_server in enumerate(self.objects):
            edge_server.capacity = capacity_values[index]

        return self.objects

    def set_update_status_all_edge_servers(self, update_status_values: list) -> list:
        """Defines the update status for edge server objects.
        Args:
            update_status_values (list): Update status values assigned to the edge server objects.
        Returns:
            edge_servers (list): Modified EdgeServer objects.
        """
        for index, edge_server in enumerate(self.objects):
            edge_server.updated = update_status_values[index]

        return self.objects
