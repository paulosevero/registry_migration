""" Contains a set of service placement heuristics.
"""
# Simulator components
from simulator.components.edge_server import EdgeServer
from simulator.components.service import Service
from simulator.components.user import User

# Python libraries
import random


def first_fit(seed: int):
    """Provisions services to the first edge servers with resources to host them.

    Args:
        seed (int): Constant value used to enable reproducibility.
    """
    # Defining a seed to enable reproducibility
    random.seed(seed)

    services = Service.all()
    edge_servers = EdgeServer.all()

    for service in services:
        for edge_server in edge_servers:
            edge_server.get_demand()
            if edge_server.capacity - edge_server.demand >= service.demand:
                edge_server.services.append(service)
                edge_server.demand += service.demand
                service.server = edge_server
                break

    # Calculating user communication paths and application delays
    for user in User.all():
        for application in user.applications:
            user.set_communication_path(app=application)
            user.compute_delay(app=application, metric="latency")


def random_fit(seed: int):
    """Provisions services to random edge servers.

    Args:
        seed (int): Constant value used to enable reproducibility.
    """
    # Defining a seed to enable reproducibility
    random.seed(seed)

    services = random.sample(Service.all(), Service.count())

    for service in services:
        edge_server = random.choice(EdgeServer.all())

        while edge_server.capacity < edge_server.demand + service.demand:
            edge_server = random.choice(EdgeServer.all())

        edge_server.services.append(service)
        edge_server.demand += service.demand
        service.server = edge_server

    # Calculating user communication paths and application delays
    for user in User.all():
        for application in user.applications:
            user.set_communication_path(app=application)
            user.compute_delay(app=application, metric="latency")
