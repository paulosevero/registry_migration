# pylint: disable=unexpected-keyword-arg,no-value-for-parameter
""" Contains container images functionality.
"""
from edge_sim_py.object_collection import ObjectCollection
import networkx as nx


class ContainerImage(ObjectCollection):
    """Class responsible for simulating container images functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None, size: int = None, name: str = "", layer: str = "") -> object:
        """Creates a ContainerImage object.

        Args:
            obj_id (int, optional): Object identifier.
            size (int, optional): Size of the container image.
            name (str, optional): Description of what kind of application the container image represents.
            layer (str, optional): Abstraction layer the container image fits in (OS, runtime, etc.).

        Returns:
            object: Created ContainerImage object.
        """
        if obj_id is None:
            obj_id = ContainerImage.count() + 1
        self.id = obj_id

        self.size = size
        self.name = name
        self.layer = layer

        self.container_registry = None

        # List that stores metadata about each migration experienced by the container image throughout the simulation
        self.available = False
        self.migrations = []

        # Reference to the Simulator object
        self.simulator = None

        # Adding the new object to the list of instances of its class
        ContainerImage.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"ContainerImage_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"ContainerImage_{self.id}"

    @classmethod
    def provision(cls, container_image: object, target_container_registry: object, path: list = []):
        """Provisions a container image inside a given container registry.

        Args:
            container_image (object): Container image that will be provisioned in a new container registry.
            target_container_registry (object): Container registry that will accommodate the image.
            path (list, optional): Network path used to transfer the image throughout the network. Defaults to [].
        """
        # Finding a network path to migrate the container image to the target host in case path is not provided
        if len(path) == 0 and container_image.container_registry is not None:
            path = nx.shortest_path(
                G=container_image.simulator.topology,
                source=container_image.container_registry.server.base_station,
                target=target_container_registry.server.base_station,
                weight="bandwidth",
            )

        # Creating a copy of the container image in the target container registry
        new_container_image = ContainerImage()
        new_container_image.size = container_image.size
        new_container_image.registry = target_container_registry
        target_container_registry.images.append(container_image)

        # Storing migration metadata
        container_image.migrations.append(
            {
                "container_image": container_image,
                "origin": container_image.container_registry,
                "destination": target_container_registry,
                "path": path,
                "start": container_image.simulator.current_step,
                "end": None,
                "data_to_transfer": container_image.size,
            }
        )

        # Adding migration metadata to each link used to transfer the container image to its target host
        for i in range(0, len(path) - 1):
            link = container_image.simulator.topology[path[i]][path[i + 1]]
            link["migrations"].append(container_image.migrations[-1])
