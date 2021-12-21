# pylint: disable=unexpected-keyword-arg,no-value-for-parameter
""" Contains container registries functionality.
"""
from edge_sim_py.object_collection import ObjectCollection


class ContainerRegistry(ObjectCollection):
    """Class responsible for simulating container registries functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None) -> object:
        """Creates a ContainerRegistry object.

        Args:
            obj_id (int, optional): Object identifier.

        Returns:
            object: Created ContainerRegistry object.
        """
        if obj_id is None:
            obj_id = ContainerRegistry.count() + 1
        self.id = obj_id

        # List of images hosted by the container registry
        self.images = []

        self.server = None

        self.available = False

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

    def demand(self) -> int:
        """Calculates the demand of a container registry.

        Returns:
            int: Container registry demand.
        """
        demand = 0

        for image in self.images:
            demand += image.size

        return demand
