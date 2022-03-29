"""
This heuristic is based on two principles:
(i) Application's delay: time it takes to communicate users to their services in the infrastructure (routing)
(ii) Application's provisioning time: time it takes to provision services in the infrastructure
    - Migration time or reprovisioning time refers to the time it takes to pull all container images that
    comprehend a service from the closest registry to the node in which we are provisioning.

References
==========
https://towardsdatascience.com/graph-machine-learning-with-python-pt-1-basics-metrics-and-algorithms-cc40972de113
https://towardsdatascience.com/community-detection-algorithms-9bd8951e7dae
https://networkx.org/documentation/stable/reference/algorithms/community.html
https://www.analyticsvidhya.com/blog/2020/04/community-detection-graphs-networks/
"""
# Simulator Components
from simulator.components.topology import Topology
from simulator.components.container_image import ContainerImage
from simulator.components.container_registry import ContainerRegistry
from simulator.components.edge_server import EdgeServer
from simulator.components.application import Application
from simulator.components.user import User

# Python Libraries
import networkx as nx


def proposed_heuristic(params: dict = {}):
    """Resource allocation strategy that migrates containerized applications and provisions container registries
    dynamically in the edge infrastructure based on users' mobility. Whenever our approach detects that provisioning
    times are growing excessively, it spins up new registries with container images used by applications accessed by
    nearby users. Conversely, idle registries are deprovisioned to avoid resource wastage.

    Args:
        params (dict, optional): User-defined parameters. Defaults to {}.
    """
    users_with_long_prov_time = []

    # Migrating services to keep them as close as possible to their users
    applications = sorted(Application.all(), key=lambda a: a.users[0].delay_slas[a] - a.users[0].delays[a])
    for application in applications:
        user = application.users[0]
        provisioning_time = 0

        delay_threshold = user.delay_slas[application] * params["delay_threshold"]
        provisioning_time_threshold = user.provisioning_time_slas[application] * params["prov_time_threshold"]

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
                        provisioning_time = service.migrate(target_server=edge_server)

                        if provisioning_time > provisioning_time_threshold:
                            users_with_long_prov_time.append(user)

                        break

            # Updating the routes used by the user to communicate with his applications
            user.set_communication_path(app=application)

    # Removing container registries that are not close to any of the users in the environment
    removing_farthest_container_registries()

    # Calculating the amount of free resources needed to host a registry
    images = []
    for image in ContainerImage.all():
        if image.name not in [img.name for img in images]:
            images.append(image)
    registry_demand = sum([img.size for img in images])

    # Gathering the list of edge servers that could host a registry
    edge_servers = [
        s for s in EdgeServer.all() if s.capacity - s.demand >= registry_demand and len(s.container_registries) == 0
    ]

    # Trying to provision registries closer to users to avoid SLA violations due to prolonged provisioning times
    while len(users_with_long_prov_time) > 0 and len(edge_servers) > 0:

        for edge_server in edge_servers:
            # List of users whose SLA violations are avoided by putting a registry on that edge server
            edge_server.supported_users = []

            for user in users_with_long_prov_time:
                path = nx.shortest_path(
                    G=Topology.first(),
                    source=edge_server.base_station,
                    target=user.base_station,
                    weight=lambda u, v, d: 1 / d["bandwidth"],
                )

                if edge_server.base_station == user.base_station:
                    provisioning_time = 0

                else:
                    # Finding the available bandwidth for the service migration
                    bandwidth = min(
                        [Topology.first()[link][path[index + 1]]["bandwidth"] for index, link in enumerate(path[:-1])]
                    )

                    # Gathering the list of images used by the user
                    user_images_demand = sum(
                        [ContainerImage.find_by("name", img).size for img in user.applications[0].services[0].layers]
                    )

                    # Calculating service's provisioning time based on the image sizes and the available network bandwidth
                    provisioning_time = user_images_demand / bandwidth

                sla = user.provisioning_time_slas[user.applications[0]]
                if provisioning_time <= sla * params["prov_time_threshold"]:
                    edge_server.supported_users.append(user)

        best_edge_server = sorted(edge_servers, key=lambda s: -len(s.supported_users))[0]

        # Provisioning a new registry in the best edge server found IF that server serves at least one user
        if len(best_edge_server.supported_users) > 0:
            new_registry = ContainerRegistry()

            for image in images:
                new_image = ContainerImage(size=image.size, name=image.name, layer=image.layer)
                new_registry.images.append(new_image)
                new_image.container_registry = new_registry

            best_edge_server.container_registries.append(new_registry)
            new_registry.server = best_edge_server
            best_edge_server.demand += new_registry.demand()

            # Updating the list of users with provisioning time issues
            for user in best_edge_server.supported_users:
                if user in users_with_long_prov_time:
                    users_with_long_prov_time.remove(user)

            # Updating the list of edge servers that could host a registry
            edge_servers.remove(best_edge_server)

        else:
            edge_servers = []


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


def removing_farthest_container_registries():
    """Deprovisions the farthest container registries in the infrastructure. We consider a container registry as one of
    the farthest registries if it is not the "closest registry" (in terms of number of hops) to any of the users.

    We use number of hops as distance measure as simulating provisioning times of each user application starting from
    each container registry would incur in a high computational complexity.
    """
    # Gathering the list of container registries that are closer to each user in the environment
    closest_registries = []
    for user in User.all():
        registries = []
        for registry in ContainerRegistry.all():
            path = nx.shortest_path(
                G=Topology.first(),
                source=registry.server.base_station,
                target=user.base_station,
                weight=lambda u, v, d: 1 / d["bandwidth"],
            )

            # Finding the available bandwidth for provisioning the user application from the current registry
            if len(path) > 1:
                bandwidth = min(
                    [Topology.first()[link][path[index + 1]]["bandwidth"] for index, link in enumerate(path[:-1])]
                )
            else:
                bandwidth = float("inf")

            registries.append({"registry": registry, "path": path, "bandwidth": bandwidth})

        closest_registry = sorted(registries, key=lambda r: -r["bandwidth"])[0]["registry"]
        if closest_registry not in closest_registries:
            closest_registries.append(closest_registry)

    # Building the list of farthest registries (i.e., registries that are not in the "closest_registries" list)
    farthest_registries = [registry for registry in ContainerRegistry.all() if registry not in closest_registries]

    # Deprovisioning farthest container registries
    for registry in farthest_registries:
        # Deprovisioning the registry from its server
        registry.server.demand -= registry.demand()
        registry.server.container_registries.remove(registry)
        registry.server = None

        # Removing the registry from the list of instances of the ContainerRegistry class
        ContainerRegistry.instances.remove(registry)

        # Removing the images from the deleted registry from the list of instances of the ContainerImage class
        for image in registry.images:
            ContainerImage.instances.remove(image)

    # Rearranging list of instances from the ContainerRegistry and ContainerImage classes
    for index, registry in enumerate(ContainerRegistry.all()):
        registry.id = index + 1

    for index, image in enumerate(ContainerImage.all()):
        image.id = index + 1
