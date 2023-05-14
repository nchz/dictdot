import re


# Helper functions.


def _is_valid_dot_key(s):
    """
    Return True if `s` can be used to access a `dictdot` key by dot notation.
    """
    return (
        s
        and type(s) is str
        and re.sub(r"\w", "", s) == ""
        and not s[0].isdigit()
        and s not in dictdot.__dict__
    )


def _build_path(*args):
    """
    Concatenate `args` to create a valid "path" to access a `dictdot` element.
    """
    result = ""
    for x in args:
        if isinstance(x, str):
            if _is_valid_dot_key(x):
                result += f".{x}"
            else:
                x = x.replace('"', r"\"")
                result += f'["{x}"]'
        else:
            result += f"[{x}]"
    return result


def _true(x):
    return True


_func = type(_true)


# Main class.


class dictdot(dict):
    """
    Python dict accessible by dot. For example:

        from dictdot import dictdot

        d = dictdot({"foo": 1})
        d.bar = 1
        assert d.foo == d["bar"]

    """

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

    @staticmethod
    def find(it, *, max_depth=0, check_key=_true, check_value=_true, prev=None):
        """
        Recursively examine `it` and yield its (nested) paths that contain keys
        and values that return True when passed as arguments to the functions
        `check_key` and `check_value`, respectively. The "paths" found by this
        function are returned as strings, hence they are not meant to be used
        programatically.

        By default `check_key` and `check_value` always return True.

        If `check_key` (or `check_value`) is an explicit function, then it will
        be applied to each key (or value).

        If `check_key` (or `check_value`) is not a function, then it will be
        replaced by a function that checks that the passed argument is equal to
        the proived `check_key` (or `check_value`). Then, `check_key="3.14"` is
        a shortcut for `check_key=lambda x: x == "3.14"`.
        """
        if prev is None:
            prev = []
        if max_depth and len(prev) >= max_depth:
            return
        if type(check_key) != _func:
            _key = check_key
            check_key = lambda x: x == _key
        if type(check_value) != _func:
            _value = check_value
            check_value = lambda x: x == _value

        if isinstance(it, dict):
            for k, v in it.items():
                if check_key(k) and check_value(v):
                    yield _build_path(*prev, k)
                yield from dictdot.find(
                    v,
                    check_key=check_key,
                    check_value=check_value,
                    prev=[*prev, k],
                    max_depth=max_depth,
                )
        elif isinstance(it, (list, tuple)):
            for i, x in enumerate(it):
                if prev and check_key(prev[-1]) and check_value(x):
                    yield _build_path(*prev, i)
                yield from dictdot.find(
                    x,
                    check_key=check_key,
                    check_value=check_value,
                    prev=[*prev, i],
                    max_depth=max_depth,
                )

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
        if name in self:
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
