import abc


class StorageServiceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "create_object")
            and callable(subclass.create_object)
            and hasattr(subclass, "save_object")
            and callable(subclass.save_object)
            and hasattr(subclass, "download_object")
            and callable(subclass.download_object)
            and hasattr(subclass, "get_object")
            and callable(subclass.get_object)
            and hasattr(subclass, "list_objects")
            and callable(subclass.list_objects)
            and hasattr(subclass, "delete_object")
            and callable(subclass.delete_object)
        )

    @abc.abstractmethod
    def create_object(self, obj_path, obj_name):
        """

        :param obj_path: path to object
        :param obj_name: name for storing object
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def save_object(self, obj_key):
        """

        :param obj_key: name for storing object
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def download_object(self, obj_name):
        """

        :param obj_name: name of object to download
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_object(self, obj_name):
        """

        :param obj_name: name of object to view
        :return:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def list_objects(self):
        """

        :param:
        :return:
        """

        raise NotImplementedError
