# Serialization to JSON

`TracingNode` can be serialized into JSON via [to_dict] method:

```python
from nicetrace import trace

with trace("my node", inputs={"x": 42}) as node:
    node.add_outputs("y", "my_result")
```

Calling ```node.to_dict()``` returns:

```python
{
  "name": "my node",
  "uid": "li7znrGkQr",
  "entries": [
    {
      "kind": "input",
      "value": 42,
      "name": "x"
    },
    {
      "kind": "output",
      "value": "my_result",
      "name": "y"
    }
  ],
  "start_time": "2024-07-08T16:26:48.619336",
  "end_time": "2024-07-08T16:26:48.619346",
  "version": "4"
}
```

When inputs or a result are not directly serializable into JSON options are provided:

### Serialization of dataclasses

Dataclasses are serialized as `dict`:

```python
from dataclasses import dataclass
from nicetrace import trace, with_trace


@dataclass
class Person:
    name: str
    age: int


@with_trace
def say_hi(person):
    return f"Hi {person.name}!"


with trace("root") as c:
    person = Person("Alice", 21)
    say_hi(person)
```

creates the following JSON description of the node:

```python
{
  "name": "root",
  "uid": "KhwWyfyqGX",
  "children": [
    {
      "name": "say_hi",
      "uid": "3cFmee7Oq7",
      "kind": "call",
      "entries": [
        {
          "kind": "input",
          "value": {
            "name": "Alice",      # <<<<<<<
            "age": 21,            # <<<<<<<
            "_type": "Person"     # <<<<<<<
          },
          "name": "person"
        },
        {
          "kind": "output",
          "value": "Hi Alice!"
        }
      ],
      "start_time": "2024-07-08T16:28:44.392553",
      "end_time": "2024-07-08T16:28:44.392573"
    }
  ],
  "start_time": "2024-07-08T16:28:44.392522",
  "end_time": "2024-07-08T16:28:44.392577",
  "version": "4"
}
```

### Method `__trace_to_node__`

A user type may define method `__trace_to_node__` to provide a custom serializer.

```python
class Person:
    name: str
    age: int

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __trace_to_node__(self):
        return {"name": self.name, "age": self.age}

person = Person("Peter", 24)
```

When `person` is serialized, the following dictionary is produced:

```python
{
    "name": "Peter",
    "age": 24,
    "_type": "Person"
}
```

### Registration of serializer

Sometimes we do not or we cannot modify a class. Registration a serializer for a given type is there for this purpose.

```python
from nicetrace import register_custom_serializer


class MyClass:
    def __init__(self, x):
        self.x = x


def myclass_serializer(m: MyClass):
    return {"x": m.x}


register_custom_serializer(MyClass, myclass_serializer)
```

### Fallback

When no mechanism above is used then only name of the type and object `id` is serialized.

E.g.:

```python
{
    "_type": "Person",
    "id": 140263930622832
}
```