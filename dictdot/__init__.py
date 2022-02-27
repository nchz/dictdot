class dictdot(dict):
    """A dict accessible by dot."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dic, recursive=True):
        """Convert `dic` to `dictdot` (nested dicts too if `recursive`)."""
        self.update(**dic)
        if recursive:
            for k, v in self.items():
                self[k] = self._nest(v)

    def _nest(self, value):
        if type(value) is dict:
            return self.__class__(value)
        elif type(value) in [list, tuple]:
            return [self._nest(v) for v in value]
        else:
            return value
