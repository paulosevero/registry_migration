""" Contains a set of methods used to create users, applications, and services."""
# Simulator components
from simulator.components.topology import Topology
from simulator.components.base_station import BaseStation
from simulator.components.user import User
from simulator.components.container_image import ContainerImage
from simulator.components.application import Application
from simulator.components.service import Service

# Component builders
from simulator.component_builders.distributions_builder import uniform

# Python libraries
import random
import typing
import networkx as nx


def user_builder(
    seed: int,
    simulation_steps: int,
    map_coordinates: list,
    number_of_objects: int,
    applications_per_user: list,
    provisioning_time_slas: list,
    delay_slas: list,
    services_per_application: list,
    service_demands: list,
    initial_service_placement: typing.Callable,
):
    """Creates a set of edge servers with user-defined capacities and power models.

    Args:
        seed (int): Constant value used to enable reproducibility.
        simulation_steps (int): Number of simulation steps.
        map_coordinates (list): Map coordinates.
        number_of_objects (int): Number of users to create.
        applications_per_user (list): Number of applications accessed by each user.
        provisioning_time_slas (list): Provisioning time SLA values for each user/application.
        delay_slas (list): Valid delay SLA values for the applications accessed by the users.
        services_per_application (list): Number of services that compose each application.
        service_demands (list): Service demand values.
        initial_service_placement (typing.Callable): Initial placement algorithm.
    """
    # Defining a seed value to enable reproducibility
    random.seed(seed)

    # Defining user mobility traces
    mobility_traces = set_mobility_traces_pathway(
        number_of_objects=number_of_objects,
        map_coordinates=map_coordinates,
        simulation_steps=simulation_steps,
    )

    # Defining the number of applications per user according to user-defined values ("applications_per_user")
    applications_per_user_values = uniform(seed=seed, n_items=number_of_objects, valid_values=applications_per_user)

    # Defining provisioning time sla values for each user according to user-defined values ("provisioning_time_slas")
    provisioning_time_sla_values = uniform(
        seed=seed, n_items=sum(applications_per_user_values), valid_values=provisioning_time_slas
    )

    # Defining delay sla values for each user according to user-defined values ("delay_slas")
    delay_sla_values = uniform(seed=seed, n_items=sum(applications_per_user_values), valid_values=delay_slas)

    # Defining the number of services per application according to user-defined values ("services_per_application")
    services_per_application_values = uniform(
        seed=seed, n_items=sum(applications_per_user_values), valid_values=services_per_application
    )

    # Defining demand values for each service according to user-defined values ("service_demands")
    service_demand_values = uniform(
        seed=seed, n_items=sum(services_per_application_values), valid_values=service_demands
    )

    # Defining container image layers for each service
    operating_systems = list(set([image for image in ContainerImage.all() if image.layer == "Operating System"]))
    runtimes = list(set([image for image in ContainerImage.all() if image.layer == "Runtime"]))
    applications = list(set([image for image in ContainerImage.all() if image.layer == "Application"]))

    n_services = sum(services_per_application_values)
    service_operating_systems = uniform(
        seed=seed, n_items=n_services, valid_values=operating_systems, shuffle_distribution=True
    )
    service_runtimes = uniform(seed=seed, n_items=n_services, valid_values=runtimes, shuffle_distribution=True)
    service_applications = uniform(seed=seed, n_items=n_services, valid_values=applications, shuffle_distribution=True)

    service_image_values = [
        [service_operating_systems[i], service_runtimes[i], service_applications[i]] for i in range(n_services)
    ]

    # Creating users, applications, and services
    create_objects(
        number_of_users=number_of_objects,
        mobility_traces=mobility_traces,
        applications_per_user_values=applications_per_user_values,
        provisioning_time_sla_values=provisioning_time_sla_values,
        delay_sla_values=delay_sla_values,
        services_per_application_values=services_per_application_values,
        service_demand_values=service_demand_values,
        service_image_values=service_image_values,
    )

    # Defining the initial service placement scheme
    initial_service_placement(seed=seed)


def set_mobility_traces_pathway(number_of_objects, map_coordinates: list, simulation_steps: int) -> list:
    """Defines the mobility trace for users according to the Pathway mobility model.

    Args:
        number_of_objects (int): Number of mobility traces to create.
        map_coordinates (list): Map coordinates.
        simulation_steps (list): Size of mobility trace (in terms of simulation steps).

    Returns:
        mobility_traces (list): User mobility traces.
    """
    mobility_traces = []

    for _ in range(number_of_objects):
        # Defines an initial location for the object
        initial_location = random.choice(map_coordinates)
        mobility_trace = [initial_location]

        while len(mobility_trace) < simulation_steps:
            # Gathering the BaseStation located in the current client's location
            current_node = BaseStation.find_by(attribute_name="coordinates", attribute_value=mobility_trace[-1])

            # Defining a target location and gathering the BaseStation located in that location
            target_position = random.choice(map_coordinates)

            target_node = BaseStation.find_by(attribute_name="coordinates", attribute_value=target_position)

            # Calculating the shortest mobility path according to the Pathway mobility model
            mobility_path = nx.shortest_path(G=Topology.first(), source=current_node, target=target_node)

            # Adding the path that connects the current to the target location to the client's mobility trace
            mobility_trace.extend([base_station.coordinates for base_station in mobility_path])

        # Slicing the client's mobility trace to match with the number of steps in
        # case the mobility path is larger than the number of simulation time steps
        if len(mobility_trace) > simulation_steps:
            number_of_unnecessary_coordinates = len(mobility_trace) - simulation_steps
            del mobility_trace[-number_of_unnecessary_coordinates:]

        mobility_traces.append(mobility_trace)

    return mobility_traces


def create_objects(
    number_of_users: int,
    mobility_traces: list,
    applications_per_user_values: list,
    provisioning_time_sla_values: list,
    delay_sla_values: list,
    services_per_application_values: list,
    service_demand_values: list,
    service_image_values: list,
):
    """Creates users, applications, and services while defining attributes for these objects.

    Args:
        number_of_users (int): Number of users to create.
        applications_per_user_values (list): Number of applications per user.
        provisioning_time_sla_values (list): Provisioning time SLA values for each user/application.
        delay_sla_values (list): Delay SLA values for each user/application.
        services_per_application_values (list): Number of services per application.
        service_demand_values (list): Demand values for each service.
        service_image_values (list): List of images that compose each service.
    """
    # Creating users
    for user_index in range(number_of_users):
        # Creating the user object
        user = User()

        # Assigning a coordinates trace to the user
        user.coordinates_trace = mobility_traces[user_index]
        user.coordinates = user.coordinates_trace[0]
        base_station = BaseStation.find_by(attribute_name="coordinates", attribute_value=user.coordinates)
        user.base_station = base_station
        base_station.users.append(user)

        # Creating applications
        for _ in range(applications_per_user_values[user_index]):
            # Creating application object
            application = Application()

            # Connecting the application to its user
            application.users.append(user)
            user.applications.append(application)

            # Assigning a delay SLA for the application
            user.delay_slas[application] = delay_sla_values[application.id - 1]

            user.provisioning_time_slas[application] = provisioning_time_sla_values[application.id - 1]

            # Creating services
            for _ in range(services_per_application_values[application.id - 1]):
                # Creating service object
                service = Service()

                # Assigning layers for the service
                service.layers = service_image_values[service.id - 1]

                # Assigning a demand for the service
                images_demand = sum([layer.size for layer in service.layers])
                service.demand = service_demand_values[service.id - 1] + images_demand

                # Connecting the service to its application
                service.application = application
                application.services.append(service)
