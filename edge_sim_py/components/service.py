# pylint: disable=unexpected-keyword-arg,no-value-for-parameter
""" Contains services functionality.
"""
from edge_sim_py.object_collection import ObjectCollection
from edge_sim_py.components.container_image import ContainerImage
import networkx as nx


class Service(ObjectCollection):
    """Class responsible for simulating services functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None, demand: int = None, layers: list = []) -> object:
        """Creates a Service object.

        Args:
            obj_id (int, optional): Object identifier.
            demand (int, optional): Service demand.

        Returns:
            object: Created Service object.
        """
        self.id = obj_id

        self.demand = demand

        self.clients = []
        self.server = None
        self.application = None

        self.layers = layers

        # List that stores metadata about each migration experienced by the service throughout the simulation
        self.migrations = []

        # Reference to the Simulator object
        self.simulator = None

        # Adding the new object to the list of instances of its class
        Service.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"Service_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"Service_{self.id}"

    def migrate(self, target_server: object, path: list = []) -> int:
        """Migrates a service to a target server.
        Args:
            target_server (object): Target server.

        Returns:
            migration_time (int): Service migration time.
        """
        # Finding a network path to migrate the service to the target host in case path is not provided
        if len(path) == 0 and self.server is not None:
            path = nx.shortest_path(
                G=self.simulator.topology,
                source=self.server.base_station,
                target=target_server.base_station,
                weight="bandwidth",
            )
        else:
            path = []

        # Calculating service migration time
        migration_time = self.get_migration_time(target_server=target_server)

        # Storing migration metadata to post-simulation analysis
        self.migrations.append(
            {
                "step": self.simulator.current_step,
                "duration": migration_time,
                "origin": self.server,
                "destination": target_server,
            }
        )

        # Removing the service from its old host
        if self.server is not None:
            self.server.demand -= self.demand
            self.server.services.remove(self)

        # Adding the service to its new host
        self.server = target_server
        self.server.demand += self.demand
        self.server.services.append(self)

        return migration_time

    def get_migration_time(self, target_server: object) -> int:
        """Calculates the time it takes to migrate a service using a given network path.

        Args:
            target_server (object): Target server.

        Returns:
            migration_time (int): Service migration time.
        """
        topology = self.simulator.topology
        selected_layers = []

        for layer in self.layers:
            layers_available = []

            for layer_available in [image for image in ContainerImage.all() if image.name == layer]:
                origin = layer_available.container_registry.server.base_station
                destination = target_server.base_station
                if origin == destination:
                    layers_available.append({"layer": layer_available, "migration_time": 0})
                else:
                    path = nx.shortest_path(
                        G=topology,
                        source=origin,
                        target=destination,
                        weight="bandwidth",
                        method="dijkstra",
                    )

                    # Finding the available bandwidth for the service migration
                    bandwidth = min(
                        [topology[link][path[index + 1]]["bandwidth"] for index, link in enumerate(path[:-1])]
                    )

                    # Calculating service migration time based on the service size and the available network bandwidth
                    migration_time = 0
                    for _ in range(len(path) - 1):
                        migration_time += layer_available.size / bandwidth

                    layers_available.append({"layer": layer_available, "migration_time": migration_time})

            best_layer_available = sorted(layers_available, key=lambda l: l["migration_time"])[0]
            selected_layers.append(best_layer_available["migration_time"])

        migration_time = sum(selected_layers)
        return migration_time
