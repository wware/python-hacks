def decorator(func):
    def wrapper(*args, **kwargs):
        print(f"{func.__name__} has been decorated!")
        return func(*args, **kwargs)
    return wrapper


def outer():
    def inner():
        return 3
    return inner()


if __name__ == '__main__':
    print(outer())
