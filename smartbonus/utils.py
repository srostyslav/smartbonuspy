

def catch_error(func):
    def wrapper(*args, **kwargs) -> (object, bool):
        if not kwargs.pop('raise_error', True):
            try:
                value = func(*args, **kwargs)
            except Exception as e:
                return e, False
            return value, True
        return func(*args, **kwargs), True
    return wrapper
