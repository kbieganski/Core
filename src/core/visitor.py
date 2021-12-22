def _qualname(obj):
    """Get the fully-qualified name of an object (including module)."""
    return obj.__module__ + '.' + obj.__qualname__

def _declaring_class(obj):
    """Get the name of the class that declared an object."""
    name = _qualname(obj)
    return name[:name.rfind('.')]

# Stores the actual visitor methods
_methods = {}

def _get_method(class_type, arg_type):
    try:
        return _methods[(_qualname(class_type), arg_type)]
    except KeyError as e:
        if len(arg_type.__bases__) == 0:
            raise e
        try:
            return _get_method(class_type, arg_type.__bases__[0])
        except KeyError as e:
            if len(class_type.__bases__) == 0:
                raise e
            return _get_method(class_type.__bases__[0], arg_type)

# Delegating visitor implementation
def _visitor_impl(self, arg):
    """Actual visitor method implementation."""
    method = _get_method(type(self), type(arg))
    return method(self, arg)

# The actual @visitor decorator
def visitor(arg_type):
    """Decorator that creates a visitor method."""

    def decorator(fn):
        declaring_class = _declaring_class(fn)
        _methods[(declaring_class, arg_type)] = fn

        # Replace all decorated methods with _visitor_impl
        return _visitor_impl

    return decorator

class Visitor:
    @visitor(object)
    def visit(self, obj):
        self.iterate(obj)

    def iterate(self, obj):
        for child in obj:
            self.visit(child)

