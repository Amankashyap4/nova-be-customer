import abc


class StorageServiceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "save")
            and callable(subclass.save)
            and hasattr(subclass, "download")
            and callable(subclass.download)
            and hasattr(subclass, "list")
            and callable(subclass.list)
            and hasattr(subclass, "delete")
            and callable(subclass.delete)
        )

    @abc.abstractmethod
    def save(self, *args):
        """

        :param args: the arguments required to save object
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def download(self, *args):
        """

        :param args: arguments required to download object
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(self):
        """

        :param:
        :return:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, obj_id):
        """

        :param: obj_id: id of object to delete
        :return:
        """

        raise NotImplementedError
