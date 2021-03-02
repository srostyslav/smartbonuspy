

def catch_error(func):
    def wrapper(*args, **kwargs):
        if not kwargs.pop('raise_error', True):
            try:
                value = func(*args, **kwargs)
            except Exception as e:
                return e, False
            return value, True
        return func(*args, **kwargs)
    return wrapper
