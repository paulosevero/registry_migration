""" Contains patch builder functionality.
"""
from edge_sim_py.component_builders.basic_builder import BasicBuilder
from edge_sim_py.components.patch import Patch


class PatchBuilder(BasicBuilder):
    """Class responsible for building patch objects."""

    def __init__(self) -> object:
        """Creates a builder responsible for creating patch objects.
        Returns:
            object: Created PatchBuilder object.
        """
        BasicBuilder.__init__(self)

    def create_objects(self, n_objects: int) -> list:
        """Creates a list of Patch objects.
        Args:
            n_objects (int): Number of Patch objects to create.
        Returns:
            list: Created Patch objects.
        """
        self.objects = [Patch(obj_id=i + 1) for i in range(n_objects)]
        return self.objects

    def set_duration_all_patches(self, duration_values: list) -> list:
        """Defines the duration for patch objects.
        Args:
            duration_values (list): Duration assigned to the patch objects.
        Returns:
            patches (list): Modified Patch objects.
        """
        for index, patch in enumerate(self.objects):
            patch.duration = duration_values[index]

        return self.objects
