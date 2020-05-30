
# Adapted from http://hackwrite.com/posts/learn-about-python-decorators-by-writing-a-function-dispatcher/
def dispatch_on_value(func):
    registry = {}

    def dispatch(value):
        try:
            return registry[value]
        except KeyError:
            return func

    def register(value, func=None):

        if func is None:
            return lambda f: register(value, f)

        registry[value] = func

        return func

    def wrapper(*args, **kwargs):
        return dispatch(args[0])(*args, **kwargs)

    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = registry

    return wrapper