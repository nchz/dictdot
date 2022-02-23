class dictdot(dict):
    """A dict accessible by dot."""

    # assign values.
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    # read values.
    def __getattribute__(self, name):
        try:
            a = getattr(dict, name)
            if hasattr(a, "__get__"):
                # bind to `self` if it's a method.
                a = a.__get__(self, dict)
            return a
        except AttributeError:
            # if `name` is not an attribute, try to return an item.
            return self.get(name)
