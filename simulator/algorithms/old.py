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
https://cdlib.readthedocs.io/en/latest/tutorial.html#tutorial
"""
# Simulator Components
from simulator.components.topology import Topology
from simulator.components.container_image import ContainerImage
from simulator.components.container_registry import ContainerRegistry
from simulator.components.edge_server import EdgeServer
from simulator.components.application import Application
from simulator.components.user import User

# Python Libraries
import random
import networkx as nx
import matplotlib.pyplot as plt

# Logging Constants
ALWAYS_PROVISION_ALL_IMAGES = False
PRINT_TOPOLOGY = False

# Heuristic Constants
DELAY_THRESHOLD = 0.8
PROVISIONING_TIME_THRESHOLD = 0.7


def get_registry_hosts_score(users: object, edge_server: object) -> float:
    topology = Topology.first()

    services_provisioned = []
    images_used = []

    for user in users:
        application = user.applications[0]
        service = application.services[0]

        new_images = []
        service_images = []

        for image_name in service.layers:
            image = ContainerImage.find_by("name", image_name)
            service_images.append(image)

            if image not in images_used:
                new_images.append(image)

        # Gathering the shortest path between the edge server's base station and the user's base station
        path = nx.shortest_path(
            G=topology,
            source=edge_server.base_station,
            target=user.base_station,
            weight="bandwidth",
            method="dijkstra",
        )

        # Calculating the approximated migration time of the best path starting from the edge server's base station
        migration_time = 0
        for _ in range(len(path) - 1):
            bandwidth = min([topology[link][path[index + 1]]["bandwidth"] for index, link in enumerate(path[:-1])])

            migration_time += sum([image.size for image in service_images]) / bandwidth

        if migration_time <= user.provisioning_time_slas[application]:
            services_provisioned.append(user)
            images_used.extend(new_images)

    return {"users_with_services_provisioned": services_provisioned, "images_used": images_used}


def proposed_heuristic():
    users_with_long_provisioning_time = []

    # Migrating services to keep them as close as possible to their users
    applications = sorted(Application.all(), key=lambda a: a.users[0].delay_slas[a] - a.users[0].delays[a])
    for application in applications:
        user = application.users[0]
        provisioning_time = 0

        delay_threshold = user.delay_slas[application] * DELAY_THRESHOLD
        provisioning_time_threshold = user.provisioning_time_slas[application] * PROVISIONING_TIME_THRESHOLD

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
                            users_with_long_provisioning_time.append(user)

                        break

            # Updating the routes used by the user to communicate with his applications
            user.set_communication_path(app=application)

    # Removing container registries that are not close to any of the users in the environment
    removing_farthest_container_registries()

    # Provisioning new container registries closer to users
    while len(users_with_long_provisioning_time) > 0:
        # Gathering the list of edge servers candidates for hosting container registries
        candidate_servers = []
        for edge_server in EdgeServer.all():

            # Calculating edge servers score based on the number of users they could serve within the expected
            # provisioning time SLAs and the number of container images they would use inside their registries
            candidate_score = get_registry_hosts_score(users=users_with_long_provisioning_time, edge_server=edge_server)

            # Filtering candidate servers. We consider valid only those candidates with capacity to accommodate
            # a registry and that manage to serve at least one user without provoking SLA violation due to
            # prolonged provisioning time
            users_with_services_provisioned = len(candidate_score["users_with_services_provisioned"])

            images_demand = sum([image.size for image in candidate_score["images_used"]])

            if edge_server.capacity >= edge_server.demand + images_demand and users_with_services_provisioned > 0:
                candidate_servers.append(
                    {
                        "edge_server": edge_server,
                        "users_with_services_provisioned": candidate_score["users_with_services_provisioned"],
                        "images_used": candidate_score["images_used"],
                    }
                )

        # Stopping the loop if there are no valid edge server candidates for hosting new container registries
        if len(candidate_servers) == 0:
            break

        # Sorting candidate servers
        candidate_servers = sorted(
            candidate_servers, key=lambda s: (-len(s["users_with_services_provisioned"]), len(s["images_used"]))
        )

        # Gathering the best candidate server based on the above sorting procedure
        best_candidate = candidate_servers[0]

        # Creating the new container registry and provisioning it in the best candidate server
        new_registry = ContainerRegistry()
        for existing_image in best_candidate["images_used"]:
            new_image = ContainerImage(
                size=existing_image.size,
                name=existing_image.name,
                layer=existing_image.layer,
            )
            new_registry.images.append(new_image)
            new_image.container_registry = new_registry

        best_candidate["edge_server"].container_registries.append(new_registry)
        new_registry.server = best_candidate["edge_server"]
        best_candidate["edge_server"].demand += new_registry.demand()

        for user in best_candidate["users_with_services_provisioned"]:
            users_with_long_provisioning_time.remove(user)


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
                source=user.base_station,
                target=registry.server.base_station,
                method="dijkstra",
            )
            registries.append({"registry": registry, "path": path})

        closest_registry = sorted(registries, key=lambda r: len(r["path"]))[0]["registry"]
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
