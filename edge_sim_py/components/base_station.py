""" Contains base station functionality.
"""
from edge_sim_py.object_collection import ObjectCollection


class BaseStation(ObjectCollection):
    """Class responsible for simulating base station functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None, coordinates: tuple = None, wireless_delay: int = None) -> object:
        """Creates an BaseStation object.

        Args:
            obj_id (int, optional): Object identifier.
            coordinates (tuple, optional): 2-tuple that represents the base station coordinates.
            wireless_delay (int, optional): Base station's wireless delay.

        Returns:
            object: Created BaseStation object.
        """
        if obj_id is None:
            obj_id = BaseStation.count() + 1
        self.id = obj_id

        self.coordinates = coordinates

        self.users = []
        self.edge_servers = []
        self.wireless_delay = wireless_delay

        # Reference to the Simulator object
        self.simulator = None

        # Adding the new object to the list of instances of its class
        BaseStation.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"BaseStation_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"BaseStation_{self.id}"
