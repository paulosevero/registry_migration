# pylint: disable=unexpected-keyword-arg,no-value-for-parameter
""" Contains container registries functionality.
"""
from edge_sim_py.object_collection import ObjectCollection
from edge_sim_py.components.container_image import ContainerImage
import networkx as nx


class ContainerRegistry(ObjectCollection):
    """Class responsible for simulating container registries functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None, base_footprint: int = None, provisioning_time: int = 0) -> object:
        """Creates a ContainerRegistry object.

        Args:
            obj_id (int, optional): Object identifier.
            base_footprint (int, optional): Amount of resources consumed by the ContainerRegistry when it's "empty".
            provisioning_time (int, optional): Amount of time needed to provisioning the ContainerRegistry.

        Returns:
            object: Created ContainerRegistry object.
        """
        if obj_id is None:
            obj_id = ContainerRegistry.count() + 1
        self.id = obj_id

        self.base_footprint = base_footprint
        self.provisioning_time = provisioning_time

        # List of images hosted by the container registry
        self.images = []

        self.server = None

        self.available = False

        # List that stores metadata about each migration experienced by the registry throughout the simulation
        self.migrations = []

        # Reference to the Simulator object
        self.simulator = None

        # Adding the new object to the list of instances of its class
        ContainerRegistry.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"ContainerRegistry_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"ContainerRegistry_{self.id}"

    def provision(self, server) -> object:
        """Provisions a container registry inside a given server.

        Args:
            server (object): Server that will host the container registry.

        Returns:
            object: [description]
        """
        # Adding the container registry to its new host
        server.container_registries.append(self)
        server.demand += self.base_footprint

    def demand(self) -> int:
        """Calculates the demand of a container registry.

        Returns:
            int: Container registry demand.
        """
        demand = self.base_footprint

        for image in self.images:
            demand += image.size

        return demand

    def replicate(self, target_server: object, images: list) -> object:
        """Replicates a container registry.

        Args:
            target_server (object): Server that will host the container registry.
            images (list): List of images to replicate in the new container registry.

        Returns:
            object: New container registry replica.
        """
        topology = self.simulator.topology

        migration_time = 0

        # Creating a new container registry replica
        new_registry = ContainerRegistry(
            base_footprint=self.base_footprint,
            provisioning_time=self.provisioning_time,
        )

        # Allocating images in the new container registry
        for image_to_replicate in images:
            image = ContainerImage(
                size=image_to_replicate.size,
                name=image_to_replicate.name,
                layer=image_to_replicate.layer,
            )
            new_registry.images.append(image)
            image.container_registry = new_registry

            path = nx.shortest_path(
                G=topology,
                source=self.server.base_station,
                target=target_server.base_station,
                weight="bandwidth",
                method="dijkstra",
            )

            # Finding the available bandwidth for the image migration
            bandwidth = min([topology[link][path[index + 1]]["bandwidth"] for index, link in enumerate(path[:-1])])

            # Calculating image migration time based on the image size and the available network bandwidth
            for _ in range(len(path) - 1):
                migration_time += image.size / bandwidth

        # Assigning the new container registry to the target server
        target_server.container_registries.append(new_registry)
        new_registry.server = target_server
        target_server.demand += new_registry.demand()

        provisioning_time = new_registry.provisioning_time + migration_time

        new_registry.migrations.append(
            {
                "step": self.simulator.current_step,
                "duration": provisioning_time,
                "origin": self.server,
                "destination": target_server,
            }
        )
        print(f"new_registry.migrations = {new_registry.migrations}")

        return new_registry
