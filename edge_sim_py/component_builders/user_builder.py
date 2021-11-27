""" Contains user builder functionality.
"""
from edge_sim_py.component_builders.basic_builder import BasicBuilder
from edge_sim_py.components.topology import Topology
from edge_sim_py.components.user import User
from edge_sim_py.components.base_station import BaseStation

import random
import networkx as nx


class UserBuilder(BasicBuilder):
    """Class responsible for building user objects."""

    def __init__(self) -> object:
        """Creates a builder responsible for creating user objects.
        Returns:
            object: Created UserBuilder object.
        """
        BasicBuilder.__init__(self)
        self.target_positions = []

    def create_objects(self, n_objects: int) -> list:
        """Creates a list of User objects.
        Args:
            n_objects (int): Number of User objects to create.
        Returns:
            list: Created User objects.
        """
        self.objects = [User(obj_id=i + 1) for i in range(n_objects)]
        return self.objects

    def set_target_positions(self, map_coordinates: list, n_target_positions: int) -> list:
        """Defines a group of positions to where users move during the simulation.

        Args:
            map_coordinates (list): Map coordinates.
            n_target_positions (int): Number of target positions to be created.

        Returns:
            target_positions (list): List of target positions.
        """
        self.target_positions = random.sample(map_coordinates, n_target_positions)
        return self.target_positions

    def set_pathway_mobility_all_users(self, map_coordinates: list, steps: int, target_positions: bool) -> list:
        """Defines the capacity for user objects.
        Args:
            map_coordinates (list): Map coordinates.
            steps (list): Size of mobility trace (in terms of number of steps).
            target_positions (bool): Using "self.target_positions" (True) or defining target positions randomly (False).
        Returns:
            users (list): Modified User objects.
        """
        for user in self.objects:
            # Defines an initial location for the object
            initial_location = random.choice(map_coordinates)
            mobility_trace = [initial_location]

            while len(mobility_trace) < steps:
                # Gathering the BaseStation located in the client's  current location
                current_node = BaseStation.find_by(attribute_name="coordinates", attribute_value=mobility_trace[-1])

                # Defining a target location and gathering the BaseStation located in that location
                if target_positions:
                    target_position = random.choice(self.target_positions)
                else:
                    target_position = random.choice(map_coordinates)

                target_node = BaseStation.find_by(attribute_name="coordinates", attribute_value=target_position)

                # Calculating the shortest mobility path according to the Pathway mobility model
                mobility_path = nx.shortest_path(G=Topology.first(), source=current_node, target=target_node)

                # Adding the path that connects the current to the target location to the client's mobility trace
                mobility_trace.extend([base_station.coordinates for base_station in mobility_path])

            # Slicing the client's mobility trace to match with the number of steps in
            # case the mobility path is larger than the number of simulation time steps
            if len(mobility_trace) > steps:
                number_of_unnecessary_coordinates = len(mobility_trace) - steps
                del mobility_trace[-number_of_unnecessary_coordinates:]

            user.coordinates_trace = mobility_trace
            user.coordinates = mobility_trace[0]

            base_station = BaseStation.find_by(attribute_name="coordinates", attribute_value=user.coordinates)
            user.base_station = base_station
            base_station.users.append(user)

        return self.objects
