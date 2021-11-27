""" Contains sanity check builder functionality.
"""
from edge_sim_py.component_builders.basic_builder import BasicBuilder
from edge_sim_py.components.sanity_check import SanityCheck


class SanityCheckBuilder(BasicBuilder):
    """Class responsible for building sanity check objects."""

    def __init__(self) -> object:
        """Creates a builder responsible for creating sanity check objects.
        Returns:
            object: Created SanityCheckBuilder object.
        """
        BasicBuilder.__init__(self)

    def create_objects(self, n_objects: int) -> list:
        """Creates a list of SanityCheck objects.
        Args:
            n_objects (int): Number of SanityCheck objects to create.
        Returns:
            list: Created SanityCheck objects.
        """
        self.objects = [SanityCheck(obj_id=i + 1) for i in range(n_objects)]
        return self.objects

    def set_duration_all_sanity_checks(self, duration_values: list) -> list:
        """Defines the duration for sanity check objects.
        Args:
            duration_values (list): Duration assigned to the sanity check objects.
        Returns:
            sanity_checks (list): Modified SanityCheck objects.
        """
        for index, sanity_check in enumerate(self.objects):
            sanity_check.duration = duration_values[index]

        return self.objects
