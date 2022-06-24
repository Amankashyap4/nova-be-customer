import enum


class ServiceEventSubscription(enum.Enum):
    """
    This class defines all events subscribed by this service. Events are created in the
    form: event_to_subscribe = {
               event_field: [field_trigger(s)]
          }
    """

    first_time_deposit = {"customer_id": "", "product_name": ""}
    new_customer_order = {"id": "", "order_by_id": "", "order_status": ""}


class ServiceEventPublishing(enum.Enum):
    """
    This class defines all events to be published by this service. Events are created in
    the form: event_name = {data_field: value_of_interest}. Above each event list various
    service subscribing to such event
    """

    # nova-be-order, nova-be-inventory
    new_customer = {"id": "", "full_name": "", "phone_number": ""}
    # nova-be-order, nova-be-inventory
    update_customer = {"id": "", "phone_number": ""}
