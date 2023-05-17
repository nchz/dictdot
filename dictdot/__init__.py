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


def _build_path(keys):
    """
    Concatenate `keys` to create a valid "path" to access a `dictdot` element.
    """
    result = ""
    for x in keys:
        if isinstance(x, str):
            if _is_valid_dot_key(x):
                result += f".{x}"
            else:
                x = x.replace('"', r"\"")
                result += f'["{x}"]'
        else:
            result += f"[{x}]"
    return result


def _true(x, prev):
    return True


_func = type(_true)


def _find(it, *, key, value, max_depth=None, prev=None):
    """
    Recursively examine `it` and yield its (nested) paths that represent keys
    and values that match the conditions defined by `key` and `value`,
    respectively.

    If `key` (or `value`) is an explicit function, it must accept 2 positional
    arguments: the key (or value) being processed, and a tuple containing all
    the keys processed so far. For example:

        def is_odd(x, prev):
            # Check if value is odd, and forget about the previous keys.
            return type(x) is int and x % 2 == 1

    You can use `prev` if your logic needs the parent keys of `x`.

    If `key` (or `value`) is not a function, then it will be replaced by a
    function that checks if its argument is equal to `key` (or `value`). Then,
    `key="some_key"` is the same as `key=lambda x, _: x == "some_key"`.

    Use `max_depth` to limit the length of the found paths.
    """
    if prev is None:
        prev = []
    if max_depth is not None and len(prev) >= max_depth:
        return
    if type(key) is not _func:
        _key = key
        key = lambda x, _: x == _key
    if type(value) is not _func:
        _value = value
        value = lambda x, _: x == _value

    if isinstance(it, dict):
        for k, v in it.items():
            if key(k, prev) and value(v, prev):
                yield (*prev, k)
            yield from _find(
                v,
                key=key,
                value=value,
                max_depth=max_depth,
                prev=(*prev, k),
            )
    elif isinstance(it, (list, tuple)):
        for i, x in enumerate(it):
            if key(i, prev) and value(x, prev):
                yield (*prev, i)
            yield from _find(
                x,
                key=key,
                value=value,
                max_depth=max_depth,
                prev=(*prev, i),
            )


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
            self[k] = self._convert(v)

    def _convert(self, value):
        """Convert dicts nested in `value` into `dictdot`."""
        if isinstance(value, dict):
            return self.__class__(value)
        elif isinstance(value, (list, tuple)):
            return [self._convert(v) for v in value]
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
        elif isinstance(value, (list, tuple)):
            return [dictdot._as_dict_recursive(v) for v in value]
        else:
            return value

    def find(self, *, max_depth=None, key=_true, value=_true, build_paths=True):
        """
        The `_find` function bound to the `dictdot` class. For details about
        the find functionality, try this:
        >>> from dictdot import _find; help(_find)

        By default, paths are built into strings that are syntactically valid
        to access `self` by dot notation. If `build_paths` is False, then yield
        tuples containing the key names for each path.
        """
        gen = _find(self, key=key, value=value, max_depth=max_depth)
        if build_paths:
            yield from map(_build_path, gen)
        else:
            yield from gen

    # Methods to handle items.

    def __setitem__(self, name, value):
        return super().__setitem__(name, self._convert(value))

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
