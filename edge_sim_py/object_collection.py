""" Adds helper methods to class objects that ease manipulation.

Example:
    'Application.first()' allows you to get the first instance from Application class.
    'User.count()' allows you to get the number of created instances from class User.
    'Service.find_by_id(3)' allows you to find the Service object that has id attribute = 3
"""


class ObjectCollection:
    """This class provides auxiliary methods that facilitate object manipulation."""

    @classmethod
    def find_by(cls, attribute_name: str, attribute_value: object) -> object:
        """Finds objects from a given class based on an user-specified attribute.

        Args:
            attribute_name (str): Attribute name.
            attribute_value (object): Attribute name.

        Returns:
            object: Class object.
        """

        class_object = next((obj for obj in cls.instances if getattr(obj, attribute_name) == attribute_value), None)
        return class_object

    @classmethod
    def find_by_id(cls, obj_id: int) -> object:
        """Finds a class object based on its ID attribute.

        Args:
            obj_id (int): Object ID.

        Returns:
            class_object (object): Class object found.
        """

        class_object = next((obj for obj in cls.instances if obj.id == obj_id), None)
        return class_object

    @classmethod
    def all(cls) -> list:
        """Returns the list of created objects of a given class.

        Returns:
            list: List of objects from a given class.
        """

        return cls.instances

    @classmethod
    def first(cls) -> object:
        """Returns the first object within the list of instances from a given class.

        Returns:
            object: Class object.
        """

        return cls.instances[0]

    @classmethod
    def count(cls) -> int:
        """Returns the number of instances from a given class.

        Returns:
            int: Number of instances from a given class.
        """

        return len(cls.instances)
