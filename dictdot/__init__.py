"""Python dict accessible by dot."""


class dictdot(dict):
    """Usage:

    from dictdot import dictdot

    d = dictdot()

    d["a"] = 1
    assert d["a"] == d.a

    d.b = 2
    assert d["b"] == d.b

    # builtin attributes are not overriden.
    d.items = "foo"
    assert d.items != d["items"]
    assert hasattr(d.items, "__call__")

    # d["NA"] will raise KeyError, but
    assert d.NA is None

    # delete by attribute name.
    del d.b
    assert "b" not in d.keys()

    # `copy` method returns a dictdot.
    d2 = d.copy()
    assert d2 == d
    assert type(d2) is dictdot

    # nested dicts are also dictdot.
    d = dictdot(
        a={"x": 0},
        b=[{"y": 1}],
    )
    assert d.a.x == d.a["x"] == d["a"].x
    assert d.b[0].y == d["b"][0]["y"]

    # even when added after init. non-dict values are not modified.
    d.c = [{"z": 2}, 2]
    assert d.c[0].z == d.c[1]

    # recursive dicts still work.
    d.c.append(d)
    assert d == d.c[-1] == d.c[-1].c[-1]
    """

    __getattr__ = dict.get
    __delattr__ = dict.__delitem__

    def __setitem__(self, name, value):
        return dict.__setitem__(self, name, self._add(value))

    def __setattr__(self, name, value):
        return self.__setitem__(name, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.items():
            self[k] = self._add(v)

    def _add(self, value):
        if type(value) is dict:
            return self.__class__(value)
        elif type(value) in [list, tuple]:
            return [self._add(v) for v in value]
        else:
            return value

    def copy(self):
        return self.__class__(dict.copy(self))
