# Python dict accessible by dot

Usage:

```python
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

# d["no_valid_key"] will raise KeyError, but
assert d.no_valid_key is None

# delete by attribute name.
del d.b
assert "b" not in d.keys()

# `copy` method will return a regular dict.
d2 = d.copy()
assert type(d2) != type(d)
assert type(d2) is dict
```
