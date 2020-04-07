def check_required_fields(dictionary, required_fields):
    errors = []
    for field in required_fields:
        try:
            dictionary[field]
        except KeyError:
            errors.append(field)
    return errors
