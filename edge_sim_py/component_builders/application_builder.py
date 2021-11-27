""" Contains application builder functionality.
"""
from edge_sim_py.component_builders.basic_builder import BasicBuilder
from edge_sim_py.components.application import Application


class ApplicationBuilder(BasicBuilder):
    """Class responsible for building application objects."""

    def __init__(self) -> object:
        """Creates a builder responsible for creating application objects.
        Returns:
            object: Created ApplicationBuilder object.
        """
        BasicBuilder.__init__(self)

    def create_objects(self, n_objects: int) -> list:
        """Creates a list of Application objects.
        Args:
            n_objects (int): Number of Application objects to create.
        Returns:
            list: Created Application objects.
        """
        self.objects = [Application(obj_id=i + 1) for i in range(n_objects)]
        return self.objects
