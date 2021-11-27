""" Contains service builder functionality.
"""
from edge_sim_py.component_builders.basic_builder import BasicBuilder
from edge_sim_py.components.service import Service


class ServiceBuilder(BasicBuilder):
    """Class responsible for building service objects."""

    def __init__(self) -> object:
        """Creates a builder responsible for creating service objects.
        Returns:
            object: Created ServiceBuilder object.
        """
        BasicBuilder.__init__(self)

    def create_objects(self, n_objects: int) -> list:
        """Creates a list of Service objects.
        Args:
            n_objects (int): Number of Service objects to create.
        Returns:
            list: Created Service objects.
        """
        self.objects = [Service(obj_id=i + 1) for i in range(n_objects)]
        return self.objects

    def set_demand_all_services(self, demand_values: list) -> list:
        """Defines the capacity for service objects.
        Args:
            demand_values (list): Demand values assigned to the service objects.
        Returns:
            services (list): Modified Service objects.
        """
        for index, service in enumerate(self.objects):
            service.demand = demand_values[index]

        return self.objects

    def set_layers_all_services(self, operating_systems: list, runtimes: list, applications: list) -> list:
        """Defines the set of container images that compose service objects.

        Args:
            operating_systems (list): List of operating system images.
            runtimes (list): List of runtime images.
            applications (list): List of application images.

        Returns:
            list: Modified list of service objects.
        """
        for index, service in enumerate(self.objects):
            # Updating the list of container layers that compose the service
            layers = [operating_systems[index], runtimes[index], applications[index]]
            service.layers = layers

            # Updating the service capacity demand based on the size of its container layers
            demand = sum([layer.size for layer in layers])
            service.demand = demand

        return self.objects
