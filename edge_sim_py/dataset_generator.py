"""Contains a set of methods used to create datasets for the simulator.

Objects are created using a group of "builders",
classes that implement the Builder design pattern to instantiate objects with different properties in an organized way.
More information about the Builder design pattern can be found in the links below:
- https://refactoring.guru/design-patterns/builder
- https://refactoring.guru/design-patterns/builder/python/example
"""
# Python libraries
import random
import json
import networkx as nx

# EdgeSimPy components
from edge_sim_py.components.base_station import BaseStation
from edge_sim_py.components.edge_server import EdgeServer
from edge_sim_py.components.application import Application
from edge_sim_py.components.service import Service
from edge_sim_py.components.topology import Topology
from edge_sim_py.components.user import User
from edge_sim_py.components.patch import Patch
from edge_sim_py.components.sanity_check import SanityCheck
from edge_sim_py.components.container_registry import ContainerRegistry
from edge_sim_py.components.container_image import ContainerImage

# Helper builders
from edge_sim_py.component_builders.map_builder import create_hexagonal_grid
from edge_sim_py.component_builders.distributions_builder import uniform
from edge_sim_py.component_builders.placements_builder import first_fit

# Component builders
from edge_sim_py.component_builders.base_station_builder import BaseStationBuilder
from edge_sim_py.component_builders.edge_server_builder import EdgeServerBuilder
from edge_sim_py.component_builders.application_builder import ApplicationBuilder
from edge_sim_py.component_builders.service_builder import ServiceBuilder
from edge_sim_py.component_builders.user_builder import UserBuilder
from edge_sim_py.component_builders.patch_builder import PatchBuilder
from edge_sim_py.component_builders.sanity_check_builder import SanityCheckBuilder
from edge_sim_py.component_builders.container_registry_builder import ContainerRegistryBuilder


VERBOSE = False

# RELEVANT VARIABLES TO CHANGE
config_simulation_steps = 20
config_SEED = 1
config_x_size = 10
config_y_size = 10
config_n_edge_servers = 30
config_n_applications = 40
config_valid_values_services_per_application = [2]
config_valid_values_edge_servers_capacity = [50, 100]
config_valid_values_service_demands = [10, 15, 20, 25]
config_valid_values_link_bandwidths = [8, 12]
config_dataset_file_name = "dataset1"


# Defining seed values to enable reproducibility
SEED = 1
random.seed(config_SEED)


# Defining number of simulation steps
simulation_steps = config_simulation_steps

# Creating list of hexagons to represent the map
map_coordinates = create_hexagonal_grid(x_size=config_x_size, y_size=config_y_size)

# Creating base stations
n_base_stations = len(map_coordinates)
base_station_builder = BaseStationBuilder()
base_station_builder.create_objects(n_objects=n_base_stations)
base_station_builder.set_coordinates_all_base_stations(coordinates=map_coordinates)
base_station_wireless_delays = uniform(n_items=n_base_stations, valid_values=[10], shuffle_distribution=True)
base_station_builder.set_wireless_delay_all_base_stations(wireless_delay_values=base_station_wireless_delays)


# Creating edge servers
n_edge_servers = config_n_edge_servers
edge_server_builder = EdgeServerBuilder()
edge_server_builder.create_objects(n_objects=n_edge_servers)
edge_servers_coordinates = random.sample(map_coordinates, n_edge_servers)
edge_server_builder.set_coordinates_all_edge_servers(coordinates=edge_servers_coordinates)
edge_servers_capacity = uniform(
    n_items=n_edge_servers, valid_values=config_valid_values_edge_servers_capacity, shuffle_distribution=True
)
edge_server_builder.set_capacity_all_edge_servers(capacity_values=edge_servers_capacity)
edge_servers_update_status = uniform(n_items=n_edge_servers, valid_values=[False], shuffle_distribution=True)
edge_server_builder.set_update_status_all_edge_servers(update_status_values=edge_servers_update_status)


# Creating container registries
n_container_registries = 6
container_registry_builder = ContainerRegistryBuilder()
container_registry_builder.create_objects(n_objects=n_container_registries)
container_registries_base_footprints = uniform(
    n_items=n_container_registries, valid_values=[1, 2], shuffle_distribution=True
)
container_registry_builder.set_base_footprint_all_container_registries(
    base_footprint_values=container_registries_base_footprints
)
container_registries_provisioning_times = uniform(
    n_items=n_container_registries, valid_values=[1, 2], shuffle_distribution=True
)
container_registry_builder.set_provisioning_time_all_container_registries(
    provisioning_time_values=container_registries_provisioning_times
)


# Creating container images
layers_of_container_images = [
    {
        "layer": "Operating System",
        "images": ["Ubuntu", "Alpine", "Debian"],
        "sizes": [10, 12, 15],
    },
    {
        "layer": "Runtime",
        "images": ["Python", "Java", "Ruby"],
        "sizes": [3, 6, 4],
    },
    {
        "layer": "Application",
        "images": ["Nginx", "MySQL", "Apache"],
        "sizes": [4, 5, 3],
    },
]

for item in layers_of_container_images:
    sizes = random.sample(item["sizes"], len(item["sizes"]))
    images = random.sample(item["images"], len(item["images"]))

    for i in range(len(images)):
        for registry in ContainerRegistry.all():
            image = ContainerImage(size=sizes[i], name=images[i], layer=item["layer"])
            image.registry = registry
            registry.images.append(image)


# Creating applications and services (and defining relationships between them)
n_applications = config_n_applications
application_builder = ApplicationBuilder()
application_builder.create_objects(n_objects=n_applications)

services_per_application = uniform(
    n_items=n_applications, valid_values=config_valid_values_services_per_application, shuffle_distribution=True
)

n_services = sum(services_per_application)
service_builder = ServiceBuilder()
service_builder.create_objects(n_objects=n_services)

operating_systems = list(set([image for image in ContainerImage.all() if image.layer == "Operating System"]))
runtimes = list(set([image for image in ContainerImage.all() if image.layer == "Runtime"]))
applications = list(set([image for image in ContainerImage.all() if image.layer == "Application"]))

service_operating_systems = uniform(n_items=n_services, valid_values=operating_systems, shuffle_distribution=True)
service_runtimes = uniform(n_items=n_services, valid_values=runtimes, shuffle_distribution=True)
service_applications = uniform(n_items=n_services, valid_values=applications, shuffle_distribution=True)

service_builder.set_layers_all_services(
    operating_systems=service_operating_systems, runtimes=service_runtimes, applications=service_applications
)

service_demands = uniform(n_items=n_services, valid_values=[1, 2, 3, 4], shuffle_distribution=True)
service_builder.set_demand_all_services(demand_values=service_demands)


for index, application in enumerate(Application.all()):
    for _ in range(services_per_application[index]):
        service = next((service for service in Service.all() if service.application is None), None)
        if service is not None:
            service.application = application
            application.services.append(service)

# Defines a random initial container registry placement scheme using
for registry in ContainerRegistry.all():
    random_server = random.choice(EdgeServer.all())

    while random_server.capacity - random_server.demand < registry.demand():
        random_server = random.choice(EdgeServer.all())

    random_server.container_registries.append(registry)
    registry.server = random_server
    random_server.demand += registry.demand()

# Defines the initial service placement scheme
first_fit()


# Creating network topology
network_nodes = BaseStation.all()
topology = Topology.new_barabasi_albert(nodes=network_nodes, seed=SEED, delay=10, bandwidth=10, min_links_per_node=1)

# Defining link attributes
n_links = len(list(topology.edges))
link_bandwidths = uniform(n_items=n_links, valid_values=config_valid_values_link_bandwidths, shuffle_distribution=True)
link_delays = uniform(n_items=n_links, valid_values=[5, 10], shuffle_distribution=True)

for link in topology.edges(data=True):
    topology[link[0]][link[1]]["bandwidth"] = link_bandwidths[0]
    topology[link[0]][link[1]]["bandwidth_demand"] = 0
    topology[link[0]][link[1]]["delay"] = link_delays[0]
    topology[link[0]][link[1]]["applications"] = []
    topology[link[0]][link[1]]["services_being_migrated"] = []

    # Updating attribute lists after the link is updated
    link_bandwidths.pop(0)
    link_delays.pop(0)


# Creating users
n_users = n_applications
user_builder = UserBuilder()
user_builder.create_objects(n_objects=n_users)
user_builder.set_target_positions(map_coordinates=map_coordinates, n_target_positions=50)
user_builder.set_pathway_mobility_all_users(
    map_coordinates=map_coordinates, steps=simulation_steps, target_positions=False
)

users_per_application = uniform(n_items=n_users, valid_values=[1], shuffle_distribution=True)

# Defining relationships between users and applications
for index, user in enumerate(User.all()):
    delay_slas = uniform(n_items=users_per_application[index], valid_values=[70, 140], shuffle_distribution=True)

    for i in range(users_per_application[index]):
        application = next((application for application in Application.all() if len(application.users) <= i), None)
        if application is not None:
            application.users.append(user)
            user.applications.append(application)
            user.delay_slas[application] = delay_slas[i]
            user.communication_paths[application] = []

# Updating users communication paths
for user in User.all():
    for application in user.applications:
        user.communication_paths[application] = []
        communication_chain = [user] + application.services

        # Defining a set of links to connect the items in the application's service chain
        for j in range(len(communication_chain) - 1):

            # Defining origin and target nodes
            origin = user.base_station if communication_chain[j] == user else communication_chain[j].server.base_station
            target = (
                user.base_station
                if communication_chain[j + 1] == user
                else communication_chain[j + 1].server.base_station
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
            user.communication_paths[application].extend(path)

        # Removing duplicated entries in the communication path to avoid NetworkX crashes
        user.communication_paths[application] = Topology.first().remove_path_duplicates(
            path=user.communication_paths[application]
        )

        # Computing the new demand of chosen links
        Topology.first().allocate_communication_path(
            communication_path=user.communication_paths[application], app=application
        )

        # The initial application delay is given by the time it takes to communicate its client and his base station
        delay = user.base_station.wireless_delay

        # Adding the communication path delay to the application's delay
        communication_path = user.communication_paths[application]
        delay += Topology.first().calculate_path_delay(path=communication_path)

        # Updating application delay inside user's 'applications' attribute
        user.delays[application] = delay


##########################
## CREATING OUTPUT FILE ##
##########################
# Creating dataset dictionary that will be converted to a JSON object
dataset = {}


# General information
dataset["simulation_steps"] = simulation_steps
dataset["coordinates_system"] = "hexagonal_grid"

# Network Power Features
# linearly proportional to link bandwidth
switch_chassis_power = 10
switch_port_active_power = 1
switch_port_low_power_percentage = 0.1
switch_power_model = "SwitchPowerModel"
switch_port_max_proportional_bandwidth = max([topology[x[0]][x[1]]["bandwidth"] for x in topology.edges(data=True)])

# Server Power Features
# linearly proportional to capacity
edge_server_max_power = 100
edge_server_static_power_percentage = 0.2
edge_server_power_model = "LinearPowerModel"
edge_server_max_proportional_capacity = max(edge_servers_capacity)


dataset["base_stations"] = [
    {
        "id": base_station.id,
        "coordinates": base_station.coordinates,
        "wireless_delay": base_station.wireless_delay,
        "users": [user.id for user in base_station.users],
        "edge_servers": [edge_server.id for edge_server in base_station.edge_servers],
        "chassis_power": switch_chassis_power,
        "power_model": switch_power_model,
    }
    for base_station in BaseStation.all()
]

dataset["edge_servers"] = [
    {
        "id": edge_server.id,
        "capacity": edge_server.capacity,
        "base_station": edge_server.base_station.id,
        "coordinates": edge_server.coordinates,
        "services": [service.id for service in edge_server.services],
        "static_power_percentage": edge_server_static_power_percentage,
        "max_power": edge_server_max_power * (edge_server.capacity / edge_server_max_proportional_capacity),
        "power_model": edge_server_power_model,
        "container_registries": [registry.id for registry in edge_server.container_registries],
    }
    for edge_server in EdgeServer.all()
]

dataset["container_images"] = [
    {
        "id": container_image.id,
        "size": container_image.size,
        "name": container_image.name,
        "layer": container_image.layer,
    }
    for container_image in ContainerImage.all()
]

dataset["container_registries"] = [
    {
        "id": container_registry.id,
        "base_footprint": container_registry.base_footprint,
        "provisioning_time": container_registry.provisioning_time,
        "server": container_registry.server.id,
        "images": [image.id for image in container_registry.images],
    }
    for container_registry in ContainerRegistry.all()
]

dataset["users"] = [
    {
        "id": user.id,
        "base_station": {"type": "BaseStation", "id": user.base_station.id},
        "applications": [
            {
                "id": app.id,
                "delay_sla": user.delay_slas[app],
                "communication_path": [
                    {"type": "BaseStation", "id": base_station.id} for base_station in user.communication_paths[app]
                ],
            }
            for app in user.applications
        ],
        "coordinates_trace": user.coordinates_trace,
    }
    for user in User.all()
]

dataset["applications"] = [
    {
        "id": application.id,
        "services": [service.id for service in application.services],
        "users": [user.id for user in application.users],
    }
    for application in Application.all()
]

dataset["services"] = [
    {
        "id": service.id,
        "demand": service.demand,
        "layers": [layer.name for layer in service.layers],
        "server": {"type": "EdgeServer", "id": service.server.id if service.server else None},
        "application": service.application.id,
    }
    for service in Service.all()
]

network_links = []
for index, link in enumerate(Topology.first().edges(data=True)):
    nodes = [
        {"type": "BaseStation", "id": link[0].id},
        {"type": "BaseStation", "id": link[1].id},
    ]
    delay = Topology.first()[link[0]][link[1]]["delay"]
    bandwidth = Topology.first()[link[0]][link[1]]["bandwidth"]
    bandwidth_demand = Topology.first()[link[0]][link[1]]["bandwidth_demand"]
    network_links.append(
        {
            "id": index + 1,
            "nodes": nodes,
            "delay": delay,
            "bandwidth": bandwidth,
            "bandwidth_demand": bandwidth_demand,
            "active_power": switch_port_active_power * (bandwidth / switch_port_max_proportional_bandwidth),
            "low_power_percentage": switch_port_low_power_percentage,
        }
    )

dataset["network"] = {"links": network_links}


# Defining output file name
dataset_file_name = config_dataset_file_name

# Storing the dataset to an output file
with open(f"datasets/{dataset_file_name}.json", "w") as output_file:
    json.dump(dataset, output_file, indent=4)
