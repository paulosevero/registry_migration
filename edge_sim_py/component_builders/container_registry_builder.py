""" Contains container registry builder functionality.
"""
from edge_sim_py.component_builders.basic_builder import BasicBuilder
from edge_sim_py.components.container_registry import ContainerRegistry


class ContainerRegistryBuilder(BasicBuilder):
    """Class responsible for building container registry objects."""

    def __init__(self) -> object:
        """Creates a builder responsible for creating container registry objects.
        Returns:
            object: Created ContainerRegistryBuilder object.
        """
        BasicBuilder.__init__(self)

    def create_objects(self, n_objects: int) -> list:
        """Creates a list of ContainerRegistry objects.
        Args:
            n_objects (int): Number of ContainerRegistry objects to create.
        Returns:
            list: Created ContainerRegistry objects.
        """
        self.objects = [ContainerRegistry(obj_id=i + 1) for i in range(n_objects)]
        return self.objects

    def set_base_footprint_all_container_registries(self, base_footprint_values: list) -> list:
        """Defines the base footprint for ContainerRegistry objects.
        Args:
            base_footprint_values (list): Base footprint values assigned to the ContainerRegistry objects.
        Returns:
            container_registries (list): Modified ContainerRegistry objects.
        """
        for index, container_registry in enumerate(self.objects):
            container_registry.base_footprint = base_footprint_values[index]

        return self.objects

    def set_provisioning_time_all_container_registries(self, provisioning_time_values: list) -> list:
        """Defines the provisioning time for ContainerRegistry objects.
        Args:
            provisioning_time_values (list): Provisioning time values assigned to the ContainerRegistry objects.
        Returns:
            container_registries (list): Modified ContainerRegistry objects.
        """
        for index, container_registry in enumerate(self.objects):
            container_registry.provisioning_time = provisioning_time_values[index]

        return self.objects
