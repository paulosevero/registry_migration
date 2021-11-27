""" Contains edge servers functionality.
"""
from edge_sim_py.object_collection import ObjectCollection


class EdgeServer(ObjectCollection):
    """Class responsible for simulating edge servers functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None, coordinates: tuple = None, capacity: int = None) -> object:
        """Creates an EdgeServer object.

        Args:
            obj_id (int, optional): Object identifier.
            coordinates (tuple, optional): 2-tuple that represents the edge server coordinates.
            capacity (int, optional): Edge server capacity.

        Returns:
            object: Created EdgeServer object.
        """
        self.id = obj_id

        self.coordinates = coordinates
        self.capacity = capacity

        self.demand = 0
        self.base_station = None

        self.being_updated = False
        self.performing_migrations = False

        self.patch = None
        self.update_metadata = {}
        self.updated = False
        self.sanity_checks = []

        self.container_registries = []

        self.max_power = 0
        self.static_power_percentage = 0
        self.power_model = None

        self.services = []

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

    def compute_demand(self):
        """Updates the edge server demand based on the services it hosts."""
        self.demand = 0

        for container_registry in self.container_registries:
            self.demand += container_registry.demand

        for service in self.services:
            self.demand += service.demand

    @classmethod
    def can_host_services(cls, servers: list, services: list) -> bool:
        """Checks if a set of servers have resources to host a group of services.

        Args:
            servers (list): List of edge servers.
            services (list): List of services that we want to accommodate inside the servers.

        Returns:
            bool: Boolean expression that tells us whether the set of servers did manage or not to host the services.
        """
        services_allocated = 0

        # Checking if all services could be hosted by the list of servers
        for service in services:
            for server in servers:
                if server.capacity >= server.demand + service.demand:
                    server.demand += service.demand
                    services_allocated += 1
                    break

        # Recomputing servers' demand
        for server in servers:
            server.compute_demand()

        return len(services) == services_allocated

    def get_power_consumption(self) -> float:
        if self.power_model is not None:
            return self.power_model.get_power_consumption(device=self)
        return 0
