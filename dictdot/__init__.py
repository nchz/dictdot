"""Python dict accessible by dot."""
import re


class dictdot(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.items():
            self[k] = self._add(v)

    def _add(self, value):
        """Convert dicts nested in `value` into `dictdot`."""
        if isinstance(value, dict):
            return self.__class__(value)
        elif isinstance(value, (list, tuple)):
            return [self._add(v) for v in value]
        else:
            return value

    def copy(self):
        return self.__class__(super().copy())

    def as_dict(self):
        """Convert `self` and nested `dictdot` objects into regular dicts."""
        return self._as_dict_recursive(self)

    @staticmethod
    def _as_dict_recursive(value):
        if isinstance(value, dictdot):
            return {k: dictdot._as_dict_recursive(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [dictdot._as_dict_recursive(v) for v in value]
        else:
            return value

    # Methods to handle items.

    def __setitem__(self, name, value):
        return super().__setitem__(name, self._add(value))

    def __setattr__(self, name, value):
        return self.__setitem__(name, value)

    def __delattr__(self, name):
        return super().__delitem__(name)

    def __getattr__(self, name):
        """
        If `name` is not a verbatim key of `self`, try to find the first key
        that matches the regex that uses "_"s in `name` as masking characters
        for "." and "-".
        """
        if name in self.__dict__:
            return self.__dict__[name]
        elif name in self:
            return self[name]
        else:
            pattern = re.compile("^" + name.replace("_", r"[\.|\-]") + "$")
            keys = [k for k in self.keys() if pattern.findall(k)]
            if keys:
                return self[keys[0]]
            else:
                return None

    # For pickling.

    def __getstate__(self):
        return self.as_dict()

    def __setstate__(self, state):
        self.update(state)
