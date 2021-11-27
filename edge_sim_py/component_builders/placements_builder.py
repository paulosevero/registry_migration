""" Contains a set of methods with service placement heuristics.
"""
# EdgeSimPy components
from edge_sim_py.components.edge_server import EdgeServer
from edge_sim_py.components.service import Service

# Python libraries
import random


def first_fit():
    """Migrates services to the first EdgeServer with resources to host it."""
    services = random.sample(Service.all(), Service.count())

    for service in services:
        for edge_server in EdgeServer.all():
            if edge_server.capacity - edge_server.demand >= service.demand:
                edge_server.services.append(service)
                edge_server.demand += service.demand
                service.server = edge_server
                break
