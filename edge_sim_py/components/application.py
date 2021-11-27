""" Contains applications functionality.
"""
from edge_sim_py.object_collection import ObjectCollection


class Application(ObjectCollection):
    """Class responsible for simulating applications functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None) -> object:
        """Creates an Application object.

        Args:
            obj_id (int, optional): Object identifier.

        Returns:
            object: Created Application object.
        """
        self.id = obj_id

        self.services = []
        self.users = []

        # Reference to the Simulator object
        self.simulator = None

        # Adding the new object to the list of instances of its class
        Application.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"Application_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"Application_{self.id}"
