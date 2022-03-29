""" Contains users functionality.
"""
from simulator.object_collection import ObjectCollection
from simulator.components.topology import Topology
from simulator.components.base_station import BaseStation
import networkx as nx


class User(ObjectCollection):
    """Class responsible for simulating users functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, obj_id: int = None, coordinates_trace: list = []) -> object:
        """Creates an User object.

        Args:
            obj_id (int, optional): Object identifier.
            coordinates_trace (list, optional): Set of user coordinates for all simulation time steps.

        Returns:
            object: Created User object.
        """
        if obj_id is None:
            obj_id = User.count() + 1
        self.id = obj_id

        self.coordinates_trace = coordinates_trace

        # User coordinates in the current simulation time step
        self.coordinates = None

        self.applications = []
        self.base_station = None

        # List of metadata from applications accessed by the user
        self.communication_paths = {}
        self.delays = {}
        self.delay_slas = {}
        self.provisioning_time_slas = {}

        # Reference to the Simulator object
        self.simulator = None

        # Adding the new object to the list of instances of its class
        User.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"User_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"User_{self.id}"

    def compute_delay(self, app: object, metric: str = "latency") -> int:
        """Computes the delay of an application accessed by the user.

        Args:
            metric (str, optional): Delay measure (valid options: 'latency' and 'response time'). Defaults to 'latency'.
            app (object): Application accessed by the user.

        Returns:
            int: Application delay.
        """
        topology = Topology.first()
        try:
            # Initializes the application's delay with the time it takes to communicate its client and his base station
            delay = self.base_station.wireless_delay

            # Adding the communication path delay to the application's delay
            communication_path = self.communication_paths[app]
            delay += topology.calculate_path_delay(path=communication_path)

            if metric.lower() == "response time":
                # We assume that Response Time = Latency * 2
                delay = delay * 2

            # Updating application delay inside user's 'applications' attribute
            self.delays[app] = delay

            return delay

        except NameError:
            print(f"App_{app.id} not accessed by User_{self.id}")

    def set_communication_path(self, app: object, communication_path: list = []) -> list:
        """Updates the set of links used during the communication of user and its application.

        Args:
            app (object): User application.
            communication_path (list, optional): User-specified communication path. Defaults to [].

        Returns:
            list: Updated communication path.
        """
        topology = Topology.first()

        # Releasing links used in the past to connect the user with its application
        if app in self.communication_paths:
            topology.release_communication_path(communication_path=self.communication_paths[app], app=app)

        # Defining communication path
        if len(communication_path) > 0:
            self.communication_paths[app] = communication_path
        else:
            self.communication_paths[app] = []
            communication_chain = [self] + app.services

            # Defining a set of links to connect the items in the application's service chain
            for i in range(len(communication_chain) - 1):

                # Defining origin and target nodes
                origin = (
                    self.base_station if communication_chain[i] == self else communication_chain[i].server.base_station
                )
                target = (
                    self.base_station
                    if communication_chain[i + 1] == self
                    else communication_chain[i + 1].server.base_station
                )

                # Finding the best communication path
                path = nx.shortest_path(
                    G=topology,
                    source=origin,
                    target=target,
                    weight="delay",
                    method="dijkstra",
                )
                # Adding the best path found to the communication path
                self.communication_paths[app].extend(path)

        # Removing duplicated entries in the communication path to avoid NetworkX crashes
        self.communication_paths[app] = topology.remove_path_duplicates(path=self.communication_paths[app])

        # Computing the new demand of chosen links
        topology.allocate_communication_path(communication_path=self.communication_paths[app], app=app)

        # Computing application's delay
        self.compute_delay(app=app, metric="latency")

        return self.communication_paths[app]

    def get_closest_base_stations(self) -> list:
        """Returns all base stations sorted by their distance (euclidean) to the user.

        Returns:
            base_stations (list): List of edge servers sorted by distance.
        """

        base_stations = [BaseStation.find_by(attribute_name="coordinates", attribute_value=self.coordinates)]
        if len(base_stations) == 0:
            base_stations = sorted(
                BaseStation.all(),
                key=lambda s: (sum([(a - b) ** 2 for a, b in zip(self.coordinates, s.coordinates)])) ** (1 / 2),
            )
        return base_stations
