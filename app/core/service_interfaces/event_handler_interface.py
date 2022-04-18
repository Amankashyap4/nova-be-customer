import abc


class EventHandlerInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "event_handler")) and callable(subclass.event_handler)

    @abc.abstractmethod
    def event_handler(self):
        """

        :param event_data: authentication data needed to retrieve valid token
        :return:
        """
        raise NotImplementedError
