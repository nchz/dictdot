import pickle
from io import BytesIO
from dictdot import dictdot


def test_find_keys_and_values():
    a = ["foo", "bar", "baz"]
    b = range(3)

    d = dictdot(zip(a, b))
    assert d.foo < d["bar"] < d.get("baz")

    d.bar = {
        "nested": 1,
        "foo": None,
        "nest": [None],
    }

    # Find every key equal to "foo".
    assert list(dictdot.find(d, check_key="foo")) == [".foo", ".bar.foo"]

    # Find every value equal to None.
    assert list(dictdot.find(d, check_value=None)) == [".bar.foo", ".bar.nest[0]"]

    # Both key and value must evaluate to True.
    assert list(dictdot.find(d, check_key="foo", check_value=None)) == [".bar.foo"]
    assert list(dictdot.find(d, check_key="bar", check_value=1)) == []


def test_assignment_and_access():
    # Assign and get values either by key or attribute.
    d = dictdot()
    d["foo"] = d.bar = 3.14
    assert d.foo == d["bar"]


def test_builtin_attributes():
    # Builtin attributes and methods are not overridden.
    d = dictdot()
    d.items = "foo"
    assert d["items"] != d.items
    assert hasattr(d.items, "__call__")
    d._add = "bar"
    assert d["_add"] != d._add
    assert hasattr(d._add, "__call__")


def test_non_existing_key():
    # Non-existing key returns None.
    d = dictdot()
    assert d.foo is None


def test_deletion():
    # Delete items by attribute name.
    d = dictdot()
    d.bar = 42
    del d.bar
    assert "bar" not in d.keys()


def test_copy():
    # copy() returns a dictdot.
    d = dictdot()
    d.foo = "bar"
    d2 = d.copy()
    assert d2 == d
    assert type(d2) is dictdot


def test_nested_dicts():
    # Nested dicts are also dictdot.
    d = dictdot(
        foo={"x": 0},
        bar=[{"y": 1}],
    )
    assert d.foo.x == d.foo["x"] == d["foo"].x
    assert d.bar[0].y == d["bar"][0]["y"]


def test_nested_dicts_after_init():
    # Even when added after initialization. Non-dict values are not modified.
    d = dictdot()
    d.foo = [{"bar": 2}, 2]
    assert d.foo[0].bar == d.foo[1]


def test_recursive_dicts():
    # Recursive dicts still work.
    d = dictdot()
    d.bar = []
    d.bar.append(d)
    assert d == d.bar[-1] == d.bar[-1].bar[-1]


def test_convert_to_dict():
    # Nested dicts are also converted.
    d = dictdot()
    d.foo = [{"bar": 1}]
    d2 = d.as_dict()
    assert d2 == d
    assert type(d2) is dict
    assert type(d2["foo"][0]) is dict


def test_keys_with_special_characters():
    # Keys with special characters can still be accessed with "_".
    d = dictdot()
    d["test-key"] = "hyphen"
    assert d.test_key == "hyphen"


def test_order_of_keys():
    # Order matters.
    d = dictdot()
    d["test.key"] = "dot"
    d["test_key"] = "underscore"
    assert d.test_key == "underscore"
    assert d["test.key"] == "dot"
    del d.test_key
    assert d.test_key == "dot"


def test_pickling():
    d = dictdot()
    d.foo = 1
    d.bar = {"x": 2}

    f = BytesIO()
    pickle.dump(d, f)
    f.seek(0)
    d2 = pickle.load(f)
    assert d2 == d
    assert type(d2) is dictdot

    f2 = BytesIO()
    pickle.dump(d2, f2)
    f2.seek(0)
    d3 = pickle.load(f2)
    assert d3 == d
    assert type(d3) is dictdot
