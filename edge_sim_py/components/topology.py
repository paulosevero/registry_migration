""" Contains topologies functionality.
"""
from edge_sim_py.object_collection import ObjectCollection
import networkx as nx


class Topology(ObjectCollection, nx.Graph):
    """Class responsible for simulating topologies functionality."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self, existing_graph=None) -> object:
        """Creates an Topology object backed by NetworkX functionality.

        Returns:
            object: Created Topology object.
        """
        # Auto increment identifier
        self.id = Topology.count() + 1

        # Reference to the Simulator object
        self.simulator = None

        # Initializing the NetworkX topology
        if existing_graph is None:
            nx.Graph.__init__(self)
        else:
            nx.Graph.__init__(self, incoming_graph_data=existing_graph)

        # Adding the new object to the list of instances of its class
        Topology.instances.append(self)

    def __str__(self):
        """Defines how the object is represented inside print statements.

        Returns:
            str: Object representation.
        """
        return f"Topology_{self.id}"

    def __repr__(self):
        """Defines how the object is represented inside the console.

        Returns:
            str: Object representation.
        """
        return f"Topology_{self.id}"

    @classmethod
    def new_barabasi_albert(cls, nodes: list, seed: int, delay: int, bandwidth: int, min_links_per_node: int) -> object:
        """Creates a network topology using the Barabási-Albert algorithm with Python objects representing graph nodes.

        Args:
            nodes (list): List of objects to be used as nodes in the topology.
            seed (int): Seed value to allow reproducibility.
            delay (int): Links delay value.
            min_links_per_node (int): Number of edges to attach from a new node to existing nodes.

        Returns:
            barabasi_albert_topology (object): Network topology built using the Barabási-Albert algorithm.
        """
        # Creating a Barabási-Albert topology using the NetworkX generator (nodes are represented by integers)
        topology = nx.barabasi_albert_graph(n=len(nodes), m=min_links_per_node, seed=seed)

        # Replacing integer nodes with user-specified Python objects (i.e., 'nodes' attribute)
        topology_with_objects_as_nodes = Topology.map_graph_nodes_to_objects(graph=topology, new_node_objects=nodes)

        # Creating an instance of the Topology class using the data from the created topology
        barabasi_albert_topology = Topology(existing_graph=topology_with_objects_as_nodes)

        # Adding attributes to the topology links
        for index, link_nodes in enumerate(barabasi_albert_topology.edges(data=True)):
            link = barabasi_albert_topology[link_nodes[0]][link_nodes[1]]
            link["id"] = index + 1
            link["delay"] = delay
            link["bandwidth"] = bandwidth
            link["demand"] = 0

        return barabasi_albert_topology

    @classmethod
    def map_graph_nodes_to_objects(cls, graph: object, new_node_objects: list) -> object:
        """Maps NetworkX graph nodes (integers by default) to Python objects. Please notice that
        this method performs the mapping according to the ordering of 'new_node_objects'.

        Args:
            graph (object): NetworkX graph object.
            new_node_objects (list): List of objects that will replace default NetworkX nodes.

        Returns:
            object: New NetworkX graph with objects as nodes.
        """
        # Creating a dictionary where NetworkX nodes represent keys and Python objects represent values
        mapping = dict(zip(graph.nodes(), new_node_objects))

        # Replacing NetworkX original nodes by Python objects
        graph = nx.relabel_nodes(graph, mapping)

        return graph

    @classmethod
    def get_overprovisioned_slices(cls, demands: list, allocated: list) -> list:
        """Calculates the leftover demand and finds items with satisfied bandwidth.

        Args:
            demands (list): List of demands (or the demand of services that will be migrated).
            allocated (list): Allocated demand for each service within the list.

        Returns:
            list, int:
        """
        overprovisioned_slices = []
        leftover_bandwidth = 0

        for i in range(len(demands)):
            if allocated[i] >= demands[i]:
                leftover_bandwidth += allocated[i] - demands[i]
                overprovisioned_slices.append(demands[i])

        return overprovisioned_slices, leftover_bandwidth

    @classmethod
    def max_min_fairness(cls, capacity: int, demands: list) -> list:
        """Calculates network allocation using the Max-Min Fairness algorithm.

        Args:
            capacity (int): Network bandwidth to be shared.
            demands (list): List of demands (e.g.: list of demands of services that will be migrated).

        Returns:
            list: Fair network allocation scheme.
        """

        # Giving a equal slice of bandwidth to each item in the demands list
        allocated_bandwidth = [capacity / len(demands)] * len(demands)

        # Calculating leftover demand and gathering items with satisfied bandwidth
        fullfilled_items, leftover_bandwidth = Topology.get_overprovisioned_slices(
            demands=demands, allocated=allocated_bandwidth
        )

        while leftover_bandwidth > 0 and len(fullfilled_items) < len(demands):
            bandwidth_to_share = leftover_bandwidth / (len(demands) - len(fullfilled_items))

            for index, demand in enumerate(demands):
                if demand in fullfilled_items:
                    # Removing overprovisioned bandwidth
                    allocated_bandwidth[index] = demand
                else:
                    # Giving a larger slice of bandwidth to items that are not fullfilled
                    allocated_bandwidth[index] += bandwidth_to_share

            # Recalculating leftover demand and gathering items with satisfied bandwidth
            fullfilled_items, leftover_bandwidth = Topology.get_overprovisioned_slices(
                demands=demands, allocated=allocated_bandwidth
            )

        allocated_bandwidth = [bw for bw in allocated_bandwidth]

        return allocated_bandwidth

    def remove_path_duplicates(self, path: list) -> list:
        """Removes side-by-side duplicated nodes on network paths to avoid NetworkX crashes.

        Args:
            path (list): Original network path.

        Returns:
            modified_path (list): Modified network path without duplicates.
        """
        modified_path = []

        for i in range(len(path)):
            if len(modified_path) == 0 or len(modified_path) >= 1 and modified_path[-1] != path[i]:
                modified_path.append(path[i])

        return modified_path

    def calculate_path_delay(self, path: list) -> int:
        """Calculates the communication delay of a network path.

        Args:
            path (list): Network path whose delay will be calculated.

        Returns:
            path_delay (int): Network path delay.
        """
        path_delay = 0

        # Removing node duplicates inside the network path that could lead to NetworkX crashes
        path = self.remove_path_duplicates(path=path)

        # Calculates the communication delay based on the delay property of each network link in the path
        for i in range(0, len(path) - 1):
            link = self[path[i]][path[i + 1]]
            path_delay += link["delay"]

        return path_delay

    def get_shortest_path(self, origin: object, target: object, user: object, app: object) -> list:
        """[summary]

        Args:
            origin (object): Origin network node.
            target (object): Destination network node.
            user (object): User that will utilize the communication path.
            app (object): Application whose data will be transferred throughout the communication path.

        Returns:
            list: Best communication path.
        """

        # Releasing the current communication path so that the currently used links have
        # equal chances to be chosen if they have enough bandwidth to accommodate the demand.
        self.release_communication_path(communication_path=user.communication_paths[app], app=app)

        shortest_path = nx.shortest_path(
            G=self,
            source=origin,
            target=target,
            weight="delay",
            method="dijkstra",
        )

        # Allocating back network links used in the application's communication path
        self.allocate_communication_path(communication_path=user.communication_paths[app], app=app)

        return shortest_path

    def release_communication_path(self, communication_path: list, app: object):
        """Releases the demand of a given application from a set of links that comprehend a communication path.

        Args:
            communication_path (list): Communication path.
            app (object): Application object.
        """
        if len(communication_path) > 1:
            for i in range(len(communication_path) - 1):
                node1 = communication_path[i]
                node2 = communication_path[i + 1]
                link = self[node1][node2]

                if app in link["applications"]:
                    link["applications"].remove(app)

    def allocate_communication_path(self, communication_path: list, app: object):
        """Adds the demand of a given application to a set of links that comprehend a communication path.

        Args:
            communication_path (list): Communication path.
            app (object): Application object.
        """
        if len(communication_path) > 1:
            for i in range(len(communication_path) - 1):
                node1 = communication_path[i]
                node2 = communication_path[i + 1]
                link = self[node1][node2]

                if app not in link["applications"]:
                    link["applications"].append(app)
