"""Contains a set of methods used to create datasets for the simulator.
"""
# Simulator components
from simulator.components import *

# Component builders
from simulator.component_builders import *

# Python libraries
import random
import json
import numpy as np

# Constant value used to enable reproducibility
SEED = 1


def create_dataset_file(dataset_filename: str, simulation_steps: int):
    """Creates a dataset file (in JSON format by default).

    Args:
        dataset_filename (str): Output filename for the dataset.
        simulation_steps (int): Number of simulation steps.
    """
    # Creating dataset dictionary that will be converted to a JSON object
    dataset = {}

    dataset["simulation_steps"] = simulation_steps

    dataset["base_stations"] = [
        {
            "id": base_station.id,
            "coordinates": base_station.coordinates,
            "wireless_delay": base_station.wireless_delay,
            "users": [user.id for user in base_station.users],
            "edge_servers": [edge_server.id for edge_server in base_station.edge_servers],
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
            "static_power_percentage": edge_server.static_power_percentage,
            "max_power": edge_server.max_power,
            "power_model": edge_server.power_model.__name__,
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
                    "provisioning_time_sla": user.provisioning_time_slas[app],
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
            "layers": [layer.name for layer in service.layers],
            "demand": service.demand,
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
            }
        )

    dataset["network"] = {"links": network_links}

    # Storing the dataset to an output file
    with open(f"datasets/{dataset_filename}.json", "w") as output_file:
        json.dump(dataset, output_file, indent=4)


# Defining a seed to enable reproducibility
np.random.seed(SEED)
random.seed(SEED)

# Defining general dataset information
dataset_filename = "dataset_25occupation"
simulation_steps = 24

# Creating the map and base stations that provide wireless connectivity to users
map_coordinates = map_builder(seed=SEED, x_size=10, y_size=10, base_stations_wireless_delays=[10])

# Creating edge servers
edge_server_builder(seed=SEED, number_of_objects=50, capacities=[700, 1400], power_models=[LinearPowerModel])

# Creating the network topology
network_builder(
    seed=SEED,
    map_coordinates=map_coordinates,
    nodes=BaseStation.all(),
    topology="Barabási-Albert",
    min_links_per_node=2,
    link_delays=[5, 10],
    link_bandwidths=[1, 2],
)

# Creating container registries and container images. Container image names were selected from the top list of popular
# images from DockerHub (categories Operating System, Programming Languages, and Databases, respectively)
container_images = [
    {"name": "Alpine", "size": 35, "layer": "Operating System"},
    {"name": "Ubuntu", "size": 40, "layer": "Operating System"},
    {"name": "Debian", "size": 45, "layer": "Operating System"},
    {"name": "CentOS", "size": 45, "layer": "Operating System"},
    {"name": "AmazonLinux", "size": 40, "layer": "Operating System"},
    {"name": "Fedora", "size": 35, "layer": "Operating System"},
    {"name": "ROS", "size": 45, "layer": "Operating System"},
    {"name": "Python", "size": 20, "layer": "Runtime"},
    {"name": "OpenJDK", "size": 30, "layer": "Runtime"},
    {"name": "golang", "size": 25, "layer": "Runtime"},
    {"name": "Ruby", "size": 25, "layer": "Runtime"},
    {"name": "bash", "size": 30, "layer": "Runtime"},
    {"name": "php", "size": 20, "layer": "Runtime"},
    {"name": "JAVA", "size": 30, "layer": "Runtime"},
    {"name": "Redis", "size": 10, "layer": "Application"},
    {"name": "MySQL", "size": 15, "layer": "Application"},
    {"name": "MongoDB", "size": 10, "layer": "Application"},
    {"name": "PostgreSQL", "size": 15, "layer": "Application"},
    {"name": "MariaDB", "size": 10, "layer": "Application"},
    {"name": "InfluxDB", "size": 5, "layer": "Application"},
    {"name": "CouchDB", "size": 10, "layer": "Application"},
]

container_registry_builder(
    seed=SEED,
    number_of_objects=15,
    images=container_images,
    placement="Random",
)

# Creating users, applications, and services
user_builder(
    seed=SEED,
    map_coordinates=map_coordinates,
    simulation_steps=simulation_steps,
    number_of_objects=55,
    applications_per_user=[1],
    provisioning_time_slas=[80, 160],
    delay_slas=[30, 60],
    services_per_application=[1],
    service_demands=[0, 0, 0],
    initial_service_placement=first_fit,
)

average_occupation_rate = 0
for edge_server in EdgeServer.all():
    average_occupation_rate += edge_server.demand * 100 / edge_server.capacity

average_occupation_rate = average_occupation_rate / EdgeServer.count()

print(f"Average Occupation Rate: {average_occupation_rate}")


create_dataset_file(dataset_filename=dataset_filename, simulation_steps=simulation_steps)
