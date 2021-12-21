"""
"""
# Simulator Components
from edge_sim_py.components.edge_server import EdgeServer
from edge_sim_py.components.application import Application

# Python Libraries
import random
import networkx as nx
import matplotlib.pyplot as plt

# Heuristic Constants
DELAY_THRESHOLD = 0.9


def display_topology(
    topology: object,
    users: list = [],
    communities: list = [],
    registries: list = [],
    save: bool = False,
    name: str = "default",
):
    """Displays network topology.

    Args:
        topology (object): Network topology object.
        users (list): List of values representing that position of users.
        communities (list): List of values representing communities in the topology.
        registries (list): List of values representing the position registries in each community in the topology.
        save (bool): Boolean value that tells the method if it needs to save an image the topology.
        name (str): Topology image file name.
    """
    # Cleaning Matplotlib's buffer
    plt.clf()

    # Customizing visual representation of topology
    positions = {}
    labels = {}
    sizes = []
    for node in topology.nodes():
        labels[node] = node.id
        positions[node] = node.coordinates
        sizes.append(250)

        if len(registries) == 0:
            if sum([len(server.container_registries) for server in node.edge_servers]) > 0:
                sizes[-1] = 1000

    # available_colors = ["blue", "red", "green", "purple", "black", "yellow"]
    available_colors = ["#" + "%06x" % random.randint(0, 0xFFFFFF) for _ in range(len(communities))]

    colors = ["black" for _ in range(len(topology.nodes))]
    for community_index, community in enumerate(communities):
        for item in community:
            item_index = list(topology.nodes()).index(item)
            colors[item_index] = available_colors[community_index]

    if len(users) == 0:
        users = list(set([user.base_station for user in User.all()]))

    for index, node in enumerate(list(topology.nodes())):
        if node in users:
            colors[index] = "red"
            sizes[index] *= 1 + len(node.users)

    for registry in registries:
        registry_index = list(topology.nodes()).index(registry)
        sizes[registry_index] = 1250

    # Configuring drawing scheme
    nx.draw(
        topology,
        pos=positions,
        node_color=colors,
        node_size=sizes,
        labels=labels,
        font_size=8,
        font_weight="bold",
        font_color="whitesmoke",
    )

    if save:
        # Saving the topology as an image file
        plt.savefig(f"{name}.png", dpi=100)
    else:
        # Displaying topology
        plt.show()


def fabio_without_registry_management():
    # Migrating services to keep services as close as possible to their users
    for application in Application.all():
        user = application.users[0]
        delay_threshold = user.delay_slas[application] * DELAY_THRESHOLD

        if user.delays[application] > delay_threshold:
            for service in application.services:
                # Finding the closest edge server that has resources to host the service
                edge_servers = get_candidate_hosts(user_base_station=user.base_station)
                for edge_server in edge_servers:
                    # Stops the search in case the edge server that hosts the service is already the closest to the user
                    if edge_server == service.server:
                        break
                    # Checks if the edge server has resources to host the service
                    elif edge_server.capacity >= edge_server.demand + service.demand:
                        service.migrate(target_server=edge_server)
                        break

            # Updating the routes used by the user to communicate with his applications
            user.set_communication_path(app=application)


def get_candidate_hosts(user_base_station):
    # Gathering the network topology object as we will need it later in the method
    topology = EdgeServer.first().simulator.topology

    edge_servers = []

    for edge_server in EdgeServer.all():
        shortest_path = nx.shortest_path(
            G=topology, source=user_base_station, target=edge_server.base_station, weight="delay"
        )
        path_delay = topology.calculate_path_delay(path=shortest_path)

        edge_servers.append({"server": edge_server, "path": shortest_path, "delay": path_delay})

    # Sorting edge servers by the delay of the shortest path between their base station and the user's base station
    edge_servers = [dict_item["server"] for dict_item in sorted(edge_servers, key=lambda e: (e["delay"]))]

    return edge_servers
