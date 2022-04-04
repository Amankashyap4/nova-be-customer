def keycloak_fields(username, obj_data):
    obj_fields = {"username": username}

    if obj_data.get("full_name"):
        fullname = obj_data.pop("full_name").split(" ")
        obj_data["first_name"] = fullname[0]
        obj_data["last_name"] = " ".join(fullname[1:])

    for field in obj_data:
        auth_service_field = field.split("_")
        for index in range(len(auth_service_field)):
            if index > 0:
                auth_service_field[index] = auth_service_field[index].capitalize()
        obj_fields["".join(auth_service_field)] = obj_data.get(field)
    return obj_fields
