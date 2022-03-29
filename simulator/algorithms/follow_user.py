""" Contains the Follow Vehicle heuristic."""
# Simulator Components
from simulator.components.edge_server import EdgeServer
from simulator.components.user import User

# Python Libraries
import networkx as nx


def follow_user(params: dict = {}):
    """Simple strategy that keeps applications as close as possible to their users. More specifically,
    whenever whenever an user move around the map, it migrates user's services to the edge server closest
    to the base station used by the user (we use network delay as proximity measure).

    Args:
        params (dict, optional): User-defined parameters. Defaults to {}.
    """
    for user in User.all():
        # Getting the list of edge servers sorted by the distance between their base stations and the user base station
        edge_servers = get_candidate_hosts(user_base_station=user.base_station)

        # Migrating services to keep them as close as possible to their users
        for application in user.applications:

            for service in application.services:
                # Finding the closest edge server that has resources to host the service
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
        shortest_path = nx.shortest_path(G=topology, source=user_base_station, target=edge_server.base_station)
        path_delay = topology.calculate_path_delay(path=shortest_path)

        edge_servers.append({"server": edge_server, "path": shortest_path, "delay": path_delay})

    # Sorting edge servers by the delay of the shortest path between their base station and the user's base station
    edge_servers = [dict_item["server"] for dict_item in sorted(edge_servers, key=lambda e: (e["delay"]))]

    return edge_servers
