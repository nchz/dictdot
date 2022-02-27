class dictdot(dict):
    """A dict accessible by dot."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
