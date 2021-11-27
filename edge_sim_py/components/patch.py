# pylint: disable=unexpected-keyword-arg,no-value-for-parameter
""" Contains patchs functionality.
"""
from edge_sim_py.object_collection import ObjectCollection


class Patch(ObjectCollection):
    """Class responsible for simulating patches functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None, duration: int = None) -> object:
        """Creates a Patch object.

        Args:
            obj_id (int, optional): Object identifier.
            duration (int, optional): Time it takes to apply the patch.

        Returns:
            object: Created Patch object.
        """
        self.id = obj_id

        # Patch duration
        self.duration = duration

        # List of sanity checks executed after the patch is applied
        self.sanity_checks = []

        # List of devices that receive the patch
        self.devices = []

        # Reference to the Simulator object
        self.simulator = None

        # Adding the new object to the list of instances of its class
        Patch.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"Patch_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"Patch_{self.id}"
