""" Contains all the simulation management functionality (dataset loading, metrics collection, etc.).
"""
# Simulator Components
from edge_sim_py.object_collection import ObjectCollection
from edge_sim_py.components.base_station import BaseStation
from edge_sim_py.components.edge_server import EdgeServer
from edge_sim_py.components.topology import Topology
from edge_sim_py.components.user import User
from edge_sim_py.components.application import Application
from edge_sim_py.components.service import Service
from edge_sim_py.components.patch import Patch
from edge_sim_py.components.sanity_check import SanityCheck
from edge_sim_py.components.container_registry import ContainerRegistry
from edge_sim_py.components.container_image import ContainerImage

# Power Features
from edge_sim_py.components.power.servers.linear_power_model import LinearPowerModel
from edge_sim_py.components.power.switches.switch_power_model import SwitchPowerModel

# Python Libraries
import json
import typing
import time
import random


class Simulator(ObjectCollection):
    """Class responsible for managing the simulation."""

    # Class attribute that allows this class to use helper methods from ObjectCollection
    instances = []

    def __init__(self):
        """Creates a Simulator object."""
        self.id = Simulator.count() + 1

        self.topology = None
        self.current_algorithm_name = ""
        self.seed = 1
        self.simulation_steps = 0
        self.current_step = 1
        self.metrics = {}
        self.original_system_state = {}
        self.stopping_criterion = None

        # Defining a seed value to enable experiments' reproducibility
        random.seed(self.seed)

        # Adding the new object to the list of instances of its class
        Simulator.instances.append(self)

    def load_dataset(self, input_file: str):
        """Spawns a simulation environment based on a dataset file.

        Args:
            input_file (str): Dataset file name.
        """
        with open(input_file, "r") as read_file:
            data = json.load(read_file)

        # Loading simulation specs
        self.simulation_steps = data["simulation_steps"]

        # Creating base stations
        if "base_stations" in data:
            for obj_data in data["base_stations"]:
                base_station = BaseStation(
                    obj_id=obj_data["id"],
                    coordinates=obj_data["coordinates"],
                    wireless_delay=obj_data["wireless_delay"],
                )

                # Power Features
                if "power_model" in obj_data:
                    base_station.chassis_power = obj_data["chassis_power"]
                    base_station.power_model = globals()[obj_data["power_model"]]

        # Creating edge servers
        if "edge_servers" in data:
            for obj_data in data["edge_servers"]:
                edge_server = EdgeServer(
                    obj_id=obj_data["id"],
                    coordinates=obj_data["coordinates"],
                    capacity=obj_data["capacity"],
                )

                if "base_station" in obj_data:
                    base_station = BaseStation.find_by_id(obj_data["base_station"])
                    edge_server.base_station = base_station
                    base_station.edge_servers.append(edge_server)

                # Power Features
                if "power_model" in obj_data:
                    edge_server.max_power = obj_data["max_power"]
                    edge_server.static_power_percentage = obj_data["static_power_percentage"]
                    edge_server.power_model = globals()[obj_data["power_model"]]

        # Creating container images
        if "container_images" in data:
            for obj_data in data["container_images"]:
                ContainerImage(
                    obj_id=obj_data["id"],
                    size=obj_data["size"],
                    name=obj_data["name"],
                    layer=obj_data["layer"],
                )

        # Creating container registries
        if "container_registries" in data:
            for obj_data in data["container_registries"]:
                registry = ContainerRegistry(
                    obj_id=obj_data["id"],
                    base_footprint=obj_data["base_footprint"],
                    provisioning_time=obj_data["provisioning_time"],
                )

                if "images" in obj_data:
                    for image_id in obj_data["images"]:
                        container_image = ContainerImage.find_by_id(image_id)
                        registry.images.append(container_image)
                        container_image.container_registry = registry

                if "server" in obj_data:
                    server = EdgeServer.find_by_id(obj_data["server"])
                    server.container_registries.append(registry)
                    registry.server = server
                    server.demand += registry.demand()

        # Creating network topology
        if "network" in data:
            topology = Topology()

            # Storing topology as an attribute of the Simulator instance
            self.topology = topology

            # Creating links
            if "links" in data["network"]:
                for obj_data in data["network"]["links"]:

                    # Finding objects that are connected by the link
                    try:
                        node1_type = obj_data["nodes"][0]["type"]
                        node2_type = obj_data["nodes"][1]["type"]
                        node1 = globals()[node1_type].find_by_id(obj_data["nodes"][0]["id"])
                        node2 = globals()[node2_type].find_by_id(obj_data["nodes"][1]["id"])
                    except TypeError:
                        print(f"Unknown node types ('{node1_type}, {node2_type}') referenced in Link_{obj_data['id']}")

                    # Adding link to the NetworkX topology
                    topology.add_edge(node1, node2)

                    # Adding link parameters
                    topology[node1][node2]["id"] = obj_data["id"]
                    topology[node1][node2]["delay"] = obj_data["delay"]
                    topology[node1][node2]["bandwidth"] = obj_data["bandwidth"]
                    topology[node1][node2]["bandwidth_demand"] = 0
                    topology[node1][node2]["applications"] = []
                    topology[node1][node2]["services_being_migrated"] = []

                    # Power Features
                    if node1.power_model != None and node2.power_model != None:
                        topology[node1][node2]["low_power_percentage"] = obj_data["low_power_percentage"]
                        topology[node1][node2]["active_power"] = obj_data["active_power"]

        # Creating applications
        if "applications" in data:
            for obj_data in data["applications"]:
                Application(obj_id=obj_data["id"])

        # Creating services
        if "services" in data:
            for obj_data in data["services"]:
                service = Service(obj_id=obj_data["id"], demand=obj_data["demand"])
                service.layers = obj_data["layers"]

                # Linking services and their applications
                if "application" in obj_data:
                    # Finding the service application by its ID
                    application = Application.find_by_id(obj_id=obj_data["application"])

                    # Connecting the service and its application
                    application.services.append(service)
                    service.application = application

                # Connecting services and edge servers
                if "server" in obj_data:
                    server = obj_data["server"]
                    # Finding the service host by its ID
                    server = globals()[server["type"]].find_by_id(server["id"])

                    # Hosting the service inside the edge server
                    server.services.append(service)
                    server.demand += service.demand
                    service.server = server

        # Creating users
        if "users" in data:
            for obj_data in data["users"]:
                user = User(
                    obj_id=obj_data["id"],
                    coordinates_trace=obj_data["coordinates_trace"],
                )

                # Adding a reference to the simulator object inside the user so that we can call topology methods below
                user.simulator = self

                # Defining user's initial location
                user.coordinates = user.coordinates_trace[0]

                # Connecting users and base stations
                if "base_station" in obj_data:
                    base_station = obj_data["base_station"]
                    # Finding the client base station by its ID
                    base_station = globals()[base_station["type"]].find_by_id(base_station["id"])

                    # Connecting the client to its base station
                    user.base_station = base_station
                    base_station.users.append(user)

                # Connecting users and applications
                applications = obj_data["applications"]
                for app_data in applications:
                    # Finding the application by its ID
                    application = Application.find_by_id(obj_id=app_data["id"])

                    # Connecting the client to the applications it consumes
                    application.users.append(user)
                    user.applications.append(application)

                    # Gathering the set of links used to communicate the client and the application
                    communication_path = []
                    for link_node_data in app_data["communication_path"]:
                        # Finding objects that form the link
                        try:
                            node_type = link_node_data["type"]
                            node = globals()[node_type].find_by_id(link_node_data["id"])
                        except TypeError:
                            print(f"Unknown node type ('{node1_type}') referenced in the communication path of {user}")
                        communication_path.append(node)

                    # Storing application's metadata inside user's attributes
                    user.set_communication_path(app=application, communication_path=communication_path)
                    user.delay_slas[application] = app_data["delay_sla"]
                    user.delays[application] = 0

    def set_simulator_attribute_inside_objects(self):
        """Adds a reference to the Simulator instance inside each created object"""
        objects = (
            Topology.all()
            + BaseStation.all()
            + EdgeServer.all()
            + Application.all()
            + Service.all()
            + User.all()
            + ContainerRegistry.all()
            + ContainerImage.all()
        )
        for obj in objects:
            obj.simulator = self

    def run(self, algorithm: typing.Callable, stopping_criterion: typing.Callable):
        """Executes the simulation.

        Args:
            algorithm (typing.Callable): Algorithm that will be executed during simulation.
            stopping_criterion (typing.Callable): Function that will determine when EdgeSimPy will stop the simulation.
        """
        self.set_simulator_attribute_inside_objects()

        # Adding a reference to the network topology inside the Simulator instance
        self.topology = Topology.first()

        # Creating an empty list to accommodate the simulation metrics
        algorithm_name = f"{str(algorithm).split(' ')[1]}-{time.time()}"
        self.current_algorithm_name = algorithm_name
        self.metrics[algorithm_name] = []

        # Storing original objects state
        self.store_original_state()

        # Resetting the simulation steps counter
        self.current_step = 1

        # Iterating over simulation time steps
        while not stopping_criterion():
            # Updating system state according to the new simulation time step
            self.update_state(step=self.current_step)

            # Collecting metrics for the current simulation step
            self.collect_metrics(algorithm=algorithm_name)

            # Executing user-specified algorithm
            algorithm()

            # Incrementing the simulation steps counter
            self.current_step += 1

        # Collecting metrics after the algorithm execution in the last simulation time step
        self.collect_metrics(algorithm=algorithm_name)

        # Restoring original objects state
        self.restore_original_state()

    def store_original_state(self):
        """Stores the original state of all objects in the simulator."""

        # Network status
        self.original_system_state["links"] = {}
        for link in self.topology.edges():
            link_data = self.topology[link[0]][link[1]]
            self.original_system_state["links"][link] = {
                "bandwidth_demand": link_data["bandwidth_demand"],
                "applications": link_data["applications"],
                "services_being_migrated": [],
            }

        # Edge servers update status
        self.original_system_state["edge_servers"] = {}
        for edge_server in EdgeServer.all():
            self.original_system_state["edge_servers"][edge_server] = {
                "updated": edge_server.updated,
                "update_metadata": edge_server.update_metadata,
            }

        # Services placement
        self.original_system_state["services"] = {}
        for service in Service.all():
            self.original_system_state["services"][service] = {"server": service.server}

        # Users locations and applications routing
        self.original_system_state["users"] = {}
        for user in User.all():
            self.original_system_state["users"][user] = {
                "base_station": user.base_station,
                "communication_paths": user.communication_paths.copy(),
            }

    def restore_original_state(self):
        """Restores the original state of all objects in the simulator."""
        # Services placement
        for service in Service.all():
            server = self.original_system_state["services"][service]["server"]
            if server is not None:
                service.migrate(target_server=server)
            service.migrations = []

        # Edge servers update status
        for edge_server in EdgeServer.all():
            edge_server.updated = self.original_system_state["edge_servers"][edge_server]["updated"]
            edge_server.update_metadata = self.original_system_state["edge_servers"][edge_server]["update_metadata"]
            edge_server.being_updated = False
            edge_server.performing_migrations = False

        # Network status
        for link in self.topology.edges():
            link_data = self.topology[link[0]][link[1]]
            link_data["bandwidth_demand"] = self.original_system_state["links"][link]["bandwidth_demand"]
            link_data["applications"] = self.original_system_state["links"][link]["applications"]
            link_data["services_being_migrated"] = []

        # Users locations and applications routing
        for user in User.all():
            user.coordinates = user.coordinates_trace[0]
            user.base_station = self.original_system_state["users"][user]["base_station"]
            for application in user.applications:
                user.set_communication_path(
                    app=application,
                    communication_path=self.original_system_state["users"][user]["communication_paths"][application],
                )

    def update_state(self, step: int):
        """Updates the system state.

        Args:
            step (int): Current simulation time step.
        """
        self.current_step = step

        # Updating users' mobility
        for user in User.all():
            if step <= len(user.coordinates_trace):
                # Updating user's location
                user.coordinates = user.coordinates_trace[step - 1]

                # Connecting the user to the closest base station
                user.base_station = user.get_closest_base_stations()[0]

                for application in user.applications:
                    # Recomputing user communication paths
                    user.set_communication_path(app=application)
                    # Updating user-perceived delay when accessing applications
                    user.compute_delay(app=application, metric="latency")

    def collect_metrics(self, algorithm: str):
        """Collects simulation metrics.

        Args:
            algorithm (str): Name of the algorithm being executed.
        """
        base_station_metrics = []
        for base_station in BaseStation.all():
            base_station_metrics.append(
                {
                    "base_station": base_station,
                    "power_consumption": base_station.get_power_consumption(),
                }
            )

        edge_server_metrics = []
        for edge_server in EdgeServer.all():
            edge_server_metrics.append(
                {
                    "edge_server": edge_server,
                    "demand": edge_server.demand,
                    "services": edge_server.services,
                    "power_consumption": edge_server.get_power_consumption(),
                }
            )

        user_metrics = []
        for user in User.all():
            user_metrics.append(
                {
                    "user": user,
                    "coordinates": user.coordinates,
                    "base_station": user.base_station,
                    "communication_paths": user.communication_paths.copy(),
                    "delays": user.delays.copy(),
                }
            )

        service_metrics = []
        for service in Service.all():
            service_metrics.append(
                {
                    "service": service,
                    "server": service.server,
                    "migrations": [
                        migration for migration in service.migrations if migration["step"] == self.current_step - 1
                    ],
                }
            )

        network_metrics = []
        for link in self.topology.edges(data=True):
            link_data = self.topology[link[0]][link[1]]
            network_metrics.append(
                {
                    "link": (link[0], link[1]),
                    "bandwidth_demand": link_data["bandwidth_demand"],
                }
            )

        # Creating the structure to accommodate simulation metrics
        self.metrics[algorithm].append(
            {
                "edge_server_metrics": edge_server_metrics,
                "base_station_metrics": base_station_metrics,
                "user_metrics": user_metrics,
                "service_metrics": service_metrics,
                "network_metrics": network_metrics,
            }
        )

    def show_results(self):
        """Displays the simulation results."""
        for algorithm, results in self.metrics.items():

            sla_violations = 0
            migrations_duration = []
            overloaded_servers = 0
            power_consumption_edge_servers = 0
            power_consumption_base_stations = 0

            for step_results in results:
                # Gathering user-related metrics
                for user_metrics in step_results["user_metrics"]:
                    user = user_metrics["user"]
                    delays = user_metrics["delays"]

                    for application in user.applications:
                        if delays[application] > user.delay_slas[application]:
                            sla_violations += 1

                # Gathering service-related metrics
                for service_metrics in step_results["service_metrics"]:
                    migrations_duration.extend([migration["duration"] for migration in service_metrics["migrations"]])

                # Gathering edge-server-related metrics
                for edge_server_metrics in step_results["edge_server_metrics"]:
                    power_consumption_edge_servers += edge_server_metrics["power_consumption"]

                    if edge_server_metrics["edge_server"].capacity < edge_server_metrics["demand"]:
                        overloaded_servers += 1

                for base_station_metrics in step_results["base_station_metrics"]:
                    power_consumption_base_stations += base_station_metrics["power_consumption"]

            number_of_migrations = len(migrations_duration)
            if number_of_migrations > 0:
                average_migration_duration = sum(migrations_duration) / len(migrations_duration)
                min_migration_duration = min(migrations_duration)
                max_migration_duration = max(migrations_duration)
            else:
                average_migration_duration = 0
                min_migration_duration = 0
                max_migration_duration = 0

            print(f"Algorithm: {algorithm}")
            print(f"    Time Steps: {self.simulation_steps}")
            print(f"    Overloaded Servers: {overloaded_servers}")
            print(f"    SLA Violations: {sla_violations}")
            print(f"    Migrations: {number_of_migrations}")
            print(f"    Average Migration Duration: {average_migration_duration}")
            print(f"    Minimum Migration Duration: {min_migration_duration}")
            print(f"    Maximum Migration Duration: {max_migration_duration}")
            print(f"    Power Consumption (Edge Servers): {power_consumption_edge_servers}")
            print(f"    Power Consumption (Base Stations): {power_consumption_base_stations}")
