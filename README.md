# dictdot

Python dict accessible by dot.

Implemented by overriding some builtin methods of regular Python `dict`.


## Example

```python
from dictdot import dictdot

d = dictdot({"foo": 1})
d.bar = 1
assert d.foo == d["bar"]
```


## Features

- Can initialize `dictdot` the same way as `dict`.
    ```python
    from dictdot import dictdot

    a = ["foo", "bar", "baz"]
    b = range(3)

    d = dictdot(zip(a, b))
    ```

- Access items by dot notation:
    ```python
    assert d.foo < d["bar"] < d.get("baz")
    ```

- After initialization, can add items either by regular item assignment, or by dot notation:
    ```python
    d.bar = {
        "nested": 1,
        "foo": None,
        "nest": [None],
    }
    ```

- Function to find keys and values nested in the dict structure:
    ```python
    # Find every key equal to "foo".
    assert list(dictdot.find(d, check_key="foo")) == [".foo", ".bar.foo"]

    # Find every value equal to None.
    assert list(dictdot.find(d, check_value=None)) == [".bar.foo", ".bar.nest[0]"]

    # Both key and value must evaluate to True.
    assert list(dictdot.find(d, check_key="foo", check_value=None)) == [".bar.foo"]
    assert list(dictdot.find(d, check_key="bar", check_value=1)) == []
    ```

- Each nested `dict` is also a `dictdot`:
    ```python
    assert type(d.bar) is dictdot
    ```

See the [tests in the source code](https://github.com/nchz/dictdot/blob/master/tests.py) for more details about the behavior and usage.
