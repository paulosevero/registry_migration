""" Contains base station builder functionality.
"""


class BasicBuilder:
    """Class responsible for building objects."""

    def __init__(self) -> object:
        """Creates a builder responsible for creating objects.
        Returns:
            object: Created Builder object.
        """
        self.objects = []
