""" Contains a set of methods used to create a container registries and container images."""
# EdgeSimPy components
from edge_sim_py.components.topology import Topology
from edge_sim_py.components.edge_server import EdgeServer
from edge_sim_py.components.container_registry import ContainerRegistry
from edge_sim_py.components.container_image import ContainerImage

# Component builders
from edge_sim_py.component_builders.distributions_builder import uniform

# Python libraries
import random
import networkx as nx
from cdlib import algorithms


def container_registry_builder(
    seed: int,
    number_of_objects: int,
    images: list,
    placement: str = "Random",
):
    """Creates a set of container registries accommodating container images.

    Args:
        seed (int): Constant value used to enable reproducibility.
        number_of_objects (int): Number of container registries to create.
        images (list): List of metadata about the container images to create.
        placement (str, optional): Initial placement scheme name. Defaults to "Random".
    """
    # Defining a seed value to enable reproducibility
    random.seed(seed)

    if placement == "Community Based":
        # Finding communities in the topology with the Louvain algorithm and re-defining the number of objects to create
        communities = algorithms.louvain(Topology.first(), resolution=1.0, randomize=False).communities
        number_of_objects = len(communities)
    else:
        communities = []

    for _ in range(number_of_objects):
        # Creating the container registry object
        container_registry = ContainerRegistry()

        # Assigning container images to the container registry
        for image_data in images:
            image = ContainerImage(size=image_data["size"], name=image_data["name"], layer=image_data["layer"])
            image.container_registry = container_registry
            container_registry.images.append(image)

    # Defining a placement scheme for container registries
    set_container_registry_placement(placement=placement, communities=communities)


def set_container_registry_placement(placement: str = "Random", communities: list = []):
    """Defines the initial placement scheme for container registries.

    Args:
        placement (str, optional): Initial container registry placement scheme name. Defaults to "Random".
        communities (list, optional): List of communities formed in the network. Defaults to [].
    """
    # Defines a random initial container registry placement
    if placement == "Random":
        for registry in ContainerRegistry.all():
            random_server = random.choice(EdgeServer.all())

            while random_server.capacity - random_server.demand < registry.demand():
                random_server = random.choice(EdgeServer.all())

            random_server.container_registries.append(registry)
            registry.server = random_server
            random_server.demand += registry.demand()

    # Defines the initial placement of container registries based on a community-based scheme
    elif placement == "Community Based":
        # Finding the best set of edge servers to accommodate container registries
        for index, registry in enumerate(ContainerRegistry.all()):
            # Creating a subgraph with the community that corresponds to the container registry
            community = communities[index]
            subgraph = Topology.first().subgraph(community)

            # Calculating the closeness centrality of nodes that belong to the subgraph (bandwidth is used as weight)
            closeness_centrality_of_nodes = nx.algorithms.centrality.closeness_centrality(
                subgraph, u=None, distance="bandwidth", wf_improved=True
            )

            # Finding the node with the highest closeness centrality with resources to accommodate the registry
            community_nodes = sorted(list(closeness_centrality_of_nodes.items()), key=lambda x: x[1], reverse=True)
            for node in community_nodes:
                if len(node[0].edge_servers) > 0:
                    edge_server = node[0].edge_servers[0]

                    if edge_server.capacity >= edge_server.get_demand() + registry.demand():
                        edge_server.container_registries.append(registry)
                        registry.server = edge_server
                        edge_server.demand += registry.demand()
                        break
