# dictdot

Python dict accessible by dot, similar to how it's done with [an object in Javascript](https://developer.mozilla.org/docs/Web/JavaScript/Reference/Global_Objects/Object).

It provides the same nature of a `dict`, plus facilities in notation and a `find` functionality that helps in the data exploration process. Particularly useful when dealing with a large JSON that you don't know much about.

Implemented by overriding some builtin methods of regular Python `dict`, it has no impact in performance or memory footprint.


## Usage

### Minimal example

```python
from dictdot import dictdot

d = dictdot()

# Get and set items either by dot or regular notation.
d["foo"] = 1
d.bar = 1
assert d.foo == d["bar"]

# Nested dicts are also converted to dictdot.
d.bar = [{"baz": 1}]
assert type(d.bar[0]) is dictdot

# Find elements by key or value.
assert [".foo", ".bar[0].baz"] == list(d.find(value=1))
```


### Performance analysis

Now let's see a more illustrative use case. We'll be using [this ~25MB JSON file](https://github.com/json-iterator/test-data/blob/master/large-file.json). If you have `curl` installed in your terminal, you can download it as follows:

```bash
curl -JO https://raw.githubusercontent.com/json-iterator/test-data/master/large-file.json
```

The following Python code can be run as it is if you have `dictdot` installed and `large-file.json` in the current directory. It will load the file in memory, then convert it to `dictdot`, and perform some `find` tasks on it, measuring the time in each step. I share the time for each step running it in my 2018 laptop (2.6GHz CPU)):

```python
import json
import time

from dictdot import dictdot

def get_time(old_t=None):
    new_t = time.time()
    if old_t:
        print(f"Time: {new_t - old_t:.2f} sec\n")
    return new_t

t = get_time()

print("Load data from file.")
with open("large-file.json") as f:
    data = json.load(f)
    t = get_time(t)
# Time: 0.36 sec

print("Convert to `dictdot`.")
data = [dictdot(d) for d in data]
t = get_time(t)
# Time: 4.67 sec

print("List all keys.")
ks = list(dictdot.find(data))
print(f"{len(ks)} keys found.")
t = get_time(t)
# 626243 keys found.
# Time: 5.53 sec

print("Find values by function.")
vs = list(dictdot.find(data, value=lambda v: type(v) is str and " dict " in v))
print(f"{len(vs)} values found.")
t = get_time(t)
# 2 values found.
# Time: 0.62 sec

print("Convert back to dict.")
dic = [d.as_dict() for d in data]
t = get_time(t)
# Time: 0.38 sec
```


### Finding values

In the example above, the variable `vs` contains paths that represent items within `data`. These items match the condition of being strings, and containing the substring `" dict "` (with trailing spaces). Let's check them:

```python
vs[0]
# '[169].payload.comment.body'

data[169].payload.comment.body
# "What about making the combined dict a local variable, like...
```


### Comparing the notation

Which prefer?

```python
vs[1]
# '[1275].payload.commits[0].message'

assert data[1275].payload.commits[0].message is \
    data[1275]["payload"]["commits"][0]["message"]
```


## Feature summary

- Can initialize `dictdot` the same way as `dict`:
    ```python
    a = ["foo", "bar", "baz"]
    b = range(3)
    d = dictdot(zip(a, b))
    ```

- Access items by dot notation, or as a `dict`:
    ```python
    assert d.foo < d["bar"] < d.get("baz")
    ```

- Also when setting an item:
    ```python
    d.bar = {
        "fee": 1,
        "boo": None,
    }
    ```

- Convert to regular `dict`:
    ```python
    d2 = d.as_dict()
    assert d == d2
    assert type(d2) is dict
    ```

- Function to find keys and values nested in the dict structure:
    ```python
    # Find every key equal to "foo".
    assert list(d.find(key="foo")) == [".foo"]

    # Find every value that bool-evaluates to False.
    assert list(d.find(value=lambda v: not v)) == [".foo", ".bar.boo"]

    # Both key and value must evaluate to True.
    assert list(d.find(key="bar", value=1)) == []
    ```

See the [tests in the source code](https://github.com/nchz/dictdot/blob/master/tests.py) for more details about the behavior and usage.
