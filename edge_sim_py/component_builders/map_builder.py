""" Contains a set of methods used to create map representations."""
# EdgeSimPy components
from edge_sim_py.components.base_station import BaseStation

# Component builders
from edge_sim_py.component_builders.distributions_builder import uniform


def map_builder(seed: int, x_size: int, y_size: int, base_stations_wireless_delays: list) -> list:
    """Constructs the map representation (dividing positions by hexagons
    by default) alongside base stations spread at each position in the map.

    Args:
        number_of_objects (int): Number of edge servers to create.
        x_size (int): Map size (x coordinates).
        y_size (int): Map size (y coordinates).
        base_stations_wireless_delays (list): Wireless delay values for base stations.

    Returns:
        map_coordinates (list): List of created map coordinates.
    """
    # Creating map coordinates
    map_coordinates = create_hexagonal_grid(x_size=x_size, y_size=y_size)

    # Defining delay values for each base station according to user-defined values ("base_stations_wireless_delays")
    wireless_delay_values = uniform(seed=seed, n_items=len(map_coordinates), valid_values=base_stations_wireless_delays)

    # Creating base stations and assigning wireless delay values to each of them
    for i in range(len(map_coordinates)):
        BaseStation(coordinates=map_coordinates[i], wireless_delay=wireless_delay_values[i])

    return map_coordinates


def create_hexagonal_grid(x_size: int, y_size: int) -> list:
    """Creates a hexagonal grid to represent the map based on [1].

    [1] Aral, Atakan, Vincenzo Demaio, and Ivona Brandic. "ARES: Reliable and Sustainable Edge
    Provisioning for Wireless Sensor Networks." IEEE Transactions on Sustainable Computing (2021).

    Args:
        x_size (int): Horizontal size of the hexagonal grid.
        y_size (int): Vertical size of the hexagonal grid.

    Returns:
        map_coordinates (list): List of created map coordinates.
    """
    map_coordinates = []

    x_range = list(range(0, x_size * 2))
    y_range = list(range(0, y_size))

    for i, y in enumerate(y_range):
        for x in x_range:
            if x % 2 == i % 2:
                map_coordinates.append((x, y))

    return map_coordinates
