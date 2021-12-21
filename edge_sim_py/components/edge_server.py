""" Contains edge servers functionality.
"""
# EdgeSimPy Components
from edge_sim_py.object_collection import ObjectCollection

# Python Libraries
import typing


class EdgeServer(ObjectCollection):
    """Class responsible for simulating edge servers functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(
        self, obj_id: int = None, coordinates: tuple = None, capacity: int = None, power_model: typing.Callable = None
    ) -> object:
        """Creates an EdgeServer object.

        Args:
            obj_id (int, optional): Object identifier.
            coordinates (tuple, optional): 2-tuple that represents the edge server coordinates.
            capacity (int, optional): Edge server capacity.
            power_model (typing.Callable, optional): Edge server power model.

        Returns:
            object: Created EdgeServer object.
        """
        if obj_id is None:
            obj_id = EdgeServer.count() + 1
        self.id = obj_id

        self.coordinates = coordinates
        self.capacity = capacity

        self.demand = 0
        self.base_station = None

        # Power Features
        self.max_power = 0
        self.static_power_percentage = 0
        self.power_model = power_model

        self.services = []
        self.container_registries = []

        # Reference to the Simulator object
        self.simulator = None

        # Adding the new object to the list of instances of its class
        EdgeServer.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"EdgeServer_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"EdgeServer_{self.id}"

    def get_demand(self) -> int:
        """Updates the edge server demand based on the services it hosts.

        Returns:
            self.demand (int): Updated edge server demand.
        """
        self.demand = 0
        for service in self.services:
            self.demand += service.demand

        for registry in self.container_registries:
            self.demand += registry.demand()

        return self.demand

    def get_power_consumption(self) -> float:
        if self.power_model is not None:
            return self.power_model.get_power_consumption(device=self)
        return 0
