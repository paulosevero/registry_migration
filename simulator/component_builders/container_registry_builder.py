""" Contains a set of methods used to create a container registries and container images."""
# Simulator components
from simulator.components.topology import Topology
from simulator.components.edge_server import EdgeServer
from simulator.components.container_registry import ContainerRegistry
from simulator.components.container_image import ContainerImage

# Component builders
from simulator.component_builders.distributions_builder import uniform

# Python libraries
import random
import networkx as nx


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

    for _ in range(number_of_objects):
        # Creating the container registry object
        container_registry = ContainerRegistry()

        # Assigning container images to the container registry
        for image_data in images:
            image = ContainerImage(size=image_data["size"], name=image_data["name"], layer=image_data["layer"])
            image.container_registry = container_registry
            container_registry.images.append(image)

    # Defining a placement scheme for container registries
    set_container_registry_placement(placement=placement)


def set_container_registry_placement(placement: str = "Random"):
    """Defines the initial placement scheme for container registries.

    Args:
        placement (str, optional): Initial container registry placement scheme name. Defaults to "Random".
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
