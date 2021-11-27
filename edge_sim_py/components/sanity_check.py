# pylint: disable=unexpected-keyword-arg,no-value-for-parameter
""" Contains sanity checks functionality.
"""
from edge_sim_py.object_collection import ObjectCollection


class SanityCheck(ObjectCollection):
    """Class responsible for simulating sanity checks functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None, duration: int = None) -> object:
        """Creates a SanityCheck object.

        Args:
            obj_id (int, optional): Object identifier.
            duration (int, optional): Time it takes to apply the sanity check.

        Returns:
            object: Created SanityCheck object.
        """
        self.id = obj_id

        # SanityCheck duration
        self.duration = duration

        # Patch that runs the sanity check
        self.patch = None

        # List of devices that receive the sanity check
        self.devices = []

        # Reference to the Simulator object
        self.simulator = None

        # Adding the new object to the list of instances of its class
        SanityCheck.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"SanityCheck_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"SanityCheck_{self.id}"
