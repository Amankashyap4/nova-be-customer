import enum


class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"
    first_time = "first_time"
    disabled = "disabled"


class IDEnum(enum.Enum):
    national_id = "national_id"
    drivers_license = "drivers_license"
    passport = "passport"
    voters_id = "voters_id"
    null = "null"


class DepositEnum(enum.Enum):
    cylinder = "cylinder"
    cash = "cash"
    cylinder_cash = "cylinder_cash"


class RegularExpression(enum.Enum):
    phone_number = r"((\+?233)((2)[03467]|(5)[045679])\d{7}$)|(((02)[03467]|(05)[045679])\d{7}$)"  # noqa
    pin = r"([0-9]{4}$)"
    token = r"([0-9]{6}$)"


class ServiceEventSubscription(enum.Enum):
    """
    This class defines all events subscribed by this service. Events are created in the
    form: event_to_subscribe = {
               event_field: [field_trigger(s)]
          }
    """

    first_time_deposit = {"customer_id": []}


class ServiceEventPublishing(enum.Enum):
    """
    This class defines all events to be published by this service. Events are created in
    the form: event_to_publish = {
                    event_field: [event_trigger(s)]
               }
    """

    create_user = {"id": []}


def status_type():
    return [status.value for status in StatusEnum]


def id_type():
    return [user_id.value for user_id in IDEnum]


def regex_type():
    reg_exp = {exp_type.name: exp_type.value for exp_type in RegularExpression}
    return reg_exp


def deposit_type():
    return [deposit.value for deposit in DepositEnum]


def events_subscribed_to():
    return [event.name for event in ServiceEventSubscription]


def fields_subscribed_to(event):
    for event_subscribed_to in ServiceEventSubscription:
        if event_subscribed_to.name == event:
            return event_subscribed_to.value.keys()


def triggers_subscribed_to(event, event_field):
    for event_subscribed_to in ServiceEventSubscription:
        if event_subscribed_to.name == event:
            return event_subscribed_to.value.get(event_field)


def events_to_publish():
    return [event.name for event in ServiceEventPublishing]


def fields_to_publish(event):
    for event_to_publish in ServiceEventPublishing:
        if event_to_publish.name == event:
            return event_to_publish.value.keys()


def triggers_to_publish(event, event_field):
    for event_to_publish in ServiceEventPublishing:
        if event_to_publish.name == event:
            return event_to_publish.value.get(event_field)
