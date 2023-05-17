import pickle
from io import BytesIO

import pytest

from dictdot import dictdot, _is_valid_dot_key, _build_path


@pytest.fixture
def d():
    return dictdot()


@pytest.fixture
def data():
    return dictdot(
        {
            "foo": 1,
            "bar": {
                "fee": 2,
            },
            "baz": [
                {
                    "foo": 1,
                    "bar": 2,
                },
            ],
        }
    )


# `find` functionality.


def test_find_all_keys(data):
    assert list(data.find(build_paths=False)) == [
        ("foo",),
        ("bar",),
        ("bar", "fee"),
        ("baz",),
        ("baz", 0),
        ("baz", 0, "foo"),
        ("baz", 0, "bar"),
    ]


def test_find_keys_and_values(data):
    # Find every key equal to "foo".
    assert list(data.find(key="foo")) == [".foo", ".baz[0].foo"]

    # Find every value equal to 2.
    assert list(data.find(value=2)) == [".bar.fee", ".baz[0].bar"]

    # Both key and value must evaluate to True.
    assert list(data.find(key="bar", value=2)) == [".baz[0].bar"]
    assert list(data.find(key="bar", value=1)) == []


def test_find_with_max_depth(data):
    assert list(data.find(max_depth=0)) == []
    # Find every key equal to "foo" with depth at most 2.
    assert (
        [".foo"]
        == list(data.find(key="foo", max_depth=1))
        == list(data.find(key="foo", max_depth=2))
    )


# Main class.


def test_assignment_and_access(d):
    # Assign and get values either by key or attribute.
    d["foo"] = d.bar = 3.14
    assert d.foo == d["bar"]


def test_non_existing_key(d):
    # Non-existing key returns None.
    assert d.foo is None
    with pytest.raises(KeyError):
        d["foo"]


def test_deletion(d):
    # Delete items by attribute name.
    d.bar = 42
    del d.bar
    assert "bar" not in d.keys()
    assert d.bar is None
    with pytest.raises(KeyError):
        d["bar"]


def test_builtin_attributes(d):
    # Builtin methods are not overridden.
    d.items = "foo"
    assert d["items"] != d.items
    assert hasattr(d.items, "__call__")
    d._convert = "bar"
    assert d["_convert"] != d._convert
    assert hasattr(d._convert, "__call__")


def test_nested_dicts(data):
    # Nested dicts are also dictdot.
    assert type(data.bar) is dictdot
    assert data.foo == data.baz[0].foo


def test_nested_dicts_after_init(d):
    # Even when added after initialization. Non-dict values are not modified.
    d.foo = [{"bar": 2}, 2]
    assert d.foo[0].bar == d.foo[1]


def test_keys_with_special_characters(d):
    # Keys with special characters can still be accessed with "_".
    d["test-key"] = "hyphen"
    assert d.test_key == "hyphen"


def test_order_of_keys(d):
    # Order matters.
    d["test.key"] = "dot"
    d["test_key"] = "underscore"
    assert d.test_key == "underscore"
    assert d["test.key"] == "dot"
    del d.test_key
    assert d.test_key == "dot"


def test_recursive_dicts(data):
    # Recursive dicts still work.
    data.baz.append(data)
    assert data is data.baz[-1] is data.baz[-1].baz[-1]


def test_copy(data):
    # copy() returns a dictdot.
    data2 = data.copy()
    assert type(data2) is dictdot
    assert data2 == data
    assert data2 is not data


def test_convert_to_dict(data):
    # Nested dicts are also converted.
    data2 = data.as_dict()
    assert data2 == data
    assert type(data2) is dict
    assert type(data2["bar"]) is dict
    assert type(data2["baz"]) is list
    assert type(data2["baz"][0]) is dict


def test_pickling(data):
    f = BytesIO()
    pickle.dump(data, f)
    f.seek(0)
    data2 = pickle.load(f)
    assert type(data2) is dictdot
    assert data2 == data
    assert data2 is not data

    f2 = BytesIO()
    pickle.dump(data2, f2)
    f2.seek(0)
    data3 = pickle.load(f2)
    assert type(data3) is dictdot
    assert data3 == data
    assert data3 is not data


def test_dict_init():
    # Can be initialized the same way as dict.
    a = ["foo", "bar", "baz"]
    b = range(3)
    d = {"foo": 0, "bar": 1, "baz": 2}
    assert d == dict(zip(a, b)) == dictdot(zip(a, b)) == dictdot(foo=0, bar=1, baz=2)


# Helper functions.


def test_is_valid_dot_key():
    assert _is_valid_dot_key("_key")
    assert not _is_valid_dot_key(None)
    assert not _is_valid_dot_key(".")
    assert not _is_valid_dot_key("0key")
    assert not _is_valid_dot_key("$key$")
    assert not _is_valid_dot_key("as_dict")
    assert not _is_valid_dot_key("copy")


def test_build_path():
    assert _build_path(["foo", "bar"]) == ".foo.bar"
    assert _build_path(["_convert", 1, "bar"]) == '["_convert"][1].bar'
    assert _build_path(['"quoted"', "'single'"]) == '["\\"quoted\\""]["\'single\'"]'
