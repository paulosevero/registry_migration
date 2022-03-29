""" Contains a set of methods used to create edge servers."""
# Simulator components
from simulator.components.base_station import BaseStation
from simulator.components.edge_server import EdgeServer

# Component builders
from simulator.component_builders.distributions_builder import uniform

# Python libraries
import random


def edge_server_builder(seed: int, number_of_objects: int, capacities: list, power_models: list = []):
    """Creates a set of edge servers with user-defined capacities and power models.

    Args:
        seed (int): Constant value used to enable reproducibility.
        number_of_objects (int): Number of edge servers to create.
        capacities (list): List of capacity values that will be assigned to the edge servers.
        power_models (list, optional): List of power models that will be assigned to the edge servers.

    Raises:
        ValueError: Number of edge servers must be less than the number of base stations.
    """
    if number_of_objects > BaseStation.count():
        raise ValueError(
            "Number of edge servers must be less than the number of base stations. Please increase the size of the map."
        )

    # Defining a seed value to enable reproducibility
    random.seed(seed)

    # Defining capacity values for each edge server according to user-defined values ("capacities")
    capacity_values = uniform(seed=seed, n_items=number_of_objects, valid_values=capacities)

    # Defining power models for each edge server according to user-defined values ("power_models")
    power_model_values = uniform(seed=seed, n_items=number_of_objects, valid_values=power_models)

    # Defining power-related attributes for edge servers
    max_power = 100
    max_proportional_capacity = max(capacity_values)
    static_power_percentage = 0.2

    for i in range(number_of_objects):
        # Picking a random base station
        base_station = random.choice([bs for bs in BaseStation.all() if len(bs.edge_servers) == 0])

        # Creating the edge server object
        edge_server = EdgeServer(capacity=capacity_values[i], power_model=power_model_values[i])

        # Assigning power-related attributes for the edge server
        edge_server.max_power = max_power * (edge_server.capacity / max_proportional_capacity)
        edge_server.static_power_percentage = static_power_percentage

        # Connecting the edge server to the base station
        edge_server.coordinates = base_station.coordinates
        edge_server.base_station = base_station
        base_station.edge_servers.append(edge_server)
