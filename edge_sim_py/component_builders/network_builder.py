""" Contains a set of methods used to create a network topology."""
# EdgeSimPy components
from edge_sim_py.components.topology import Topology

# Component builders
from edge_sim_py.component_builders.distributions_builder import uniform

# Python libraries
import networkx as nx


def find_neighbors_hexagonal_grid(map_coordinates: list, current_position: tuple) -> list:
    """Finds the set of adjacent positions of coordinates 'current_position' in a hexagonal grid.

    Args:
        map_coordinates (list): List of map coordinates.
        current_position (tuple): Current position in the map.

    Returns:
        neighbors (list): List of neighbor positions.
    """
    x = current_position[0]
    y = current_position[1]

    candidates = [(x - 2, y), (x - 1, y + 1), (x + 1, y + 1), (x + 2, y), (x + 1, y - 1), (x - 1, y - 1)]

    neighbors = [
        neighbor
        for neighbor in candidates
        if neighbor[0] >= 0 and neighbor[1] >= 0 and (neighbor[0], neighbor[1]) in map_coordinates
    ]

    return neighbors


def network_builder(
    seed: int,
    map_coordinates: list,
    nodes: list,
    link_delays: list,
    link_bandwidths: list,
    topology: str = "Barabási-Albert",
    min_links_per_node: int = 1,
):
    """Creates a network infrastructure with user-defined topology, link delay and capacities, and power models.

    Args:
        seed (int): Constant value used to enable reproducibility.
        map_coordinates (list): List of map coordinates.
        nodes (list): List of objects that will compose the network infrastructure.
        link_delays (list): Delay values that will be assigned to the network links.
        link_bandwidths (list): Bandwidth values that will be assigned to the network links.
        topology (str, optional): Network topology name. Defaults to "Barabási-Albert".
        min_links_per_node (int, optional): Minimum number of links per network node. Defaults to 1.
    """
    # Creating the network topology
    topology = create_topology(
        map_coordinates=map_coordinates, topology=topology, nodes=nodes, min_links_per_node=min_links_per_node
    )

    # Defining delay and bandwidth values for each link according to user-defined values ("link_delays", "link_bandwidths")
    delay_values = uniform(seed=seed, n_items=len(topology.edges()), valid_values=link_delays)
    bandwidth_values = uniform(seed=seed, n_items=len(topology.edges()), valid_values=link_bandwidths)

    # Adding attributes to network links
    for i, link_nodes in enumerate(topology.edges(data=True)):
        link = topology[link_nodes[0]][link_nodes[1]]
        link["id"] = i + 1
        link["delay"] = delay_values[i]
        link["bandwidth"] = bandwidth_values[i]
        link["bandwidth_demand"] = 0
        link["applications"] = []
        link["services_being_migrated"] = []


def create_topology(
    map_coordinates: list, nodes: list, topology: str = "Barabási-Albert", min_links_per_node: int = 1
) -> object:
    """Creates a network topology.

    Args:
        map_coordinates (list): List of map coordinates.
        nodes (list): List of nodes that will compose the network topology.
        topology (str, optional): Network topology name. Defaults to "Barabási-Albert".
        min_links_per_node (int, optional): Minimum number of links per network node. Defaults to 1.

    Raises:
        ValueError: Invalid topology name.

    Returns:
        object: Created topology object.
    """
    valid_topology_names = ["Barabási-Albert", "Hexagonal Lattice"]
    if topology not in valid_topology_names:
        raise ValueError(f"Invalid topology name. Valid options: {valid_topology_names}")

    if topology == "Barabási-Albert":
        # Creating topology
        topology = nx.barabasi_albert_graph(n=len(nodes), m=min_links_per_node, seed=1)

    elif topology == "Hexagonal Lattice":
        # Creating nodes
        topology = nx.Graph()
        topology.add_nodes_from(map_coordinates)

        # Adding links connecting nodes
        for coordinates in map_coordinates:
            neighbors = find_neighbors_hexagonal_grid(map_coordinates=map_coordinates, current_position=coordinates)
            for neighbor in neighbors:
                topology.add_edge(coordinates, neighbor)

    # Replacing default node types (integers) with user-specified Python objects (i.e., 'nodes' parameter)
    topology = Topology.map_graph_nodes_to_objects(graph=topology, new_node_objects=nodes)
    topology = Topology(existing_graph=topology)

    return topology
