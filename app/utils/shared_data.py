def extract_valid_data(obj_data: dict, validator):
    valid_data = dict()
    for field in validator:
        valid_data[field] = obj_data.get(field)
    return valid_data
