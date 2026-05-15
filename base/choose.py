def first_non_empty(*values):
    for value in values:
        if value:
            return value
    return None
