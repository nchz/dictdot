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
        a={
            "x": 0,
            "y": 0,
        },
        b=[
            {"w": 1},
            {"z": 2},
        ],
    )
    assert d["a"]["x"] == d.a.y
    assert d.b[0].w == 1
    assert d.b[0].z is None
    assert d.b[1].z == 2
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.items():
            self[k] = self._nest(v)

    def _nest(self, value):
        if type(value) is dict:
            return self.__class__(value)
        elif type(value) in [list, tuple]:
            return [self._nest(v) for v in value]
        else:
            return value

    def copy(self):
        return self.__class__(dict.copy(self))
