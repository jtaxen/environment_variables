# Environment variables

![pytest](https://github.com/jtaxen/environment_variables/actions/workflows/pytest.yml/badge.svg)
[![pypi](https://img.shields.io/pypi/v/environment_variables.svg)](https://pypi.python.org/project/environment_variables)
[![license](https://img.shields.io/github/license/jtaxen/environment_variables.svg)](https://github.com/jtaxen/environment_variables/blob/main/LICENSE)

Enum style access to environment variables with type annotations

~ Av vars och env efter förmåga,
  åt vars och env efter behov ~

The package is hosted at [PyPI](https://pypi.org/project/environment-variables/)

## Documentation

The documentation can be found on [ReadTheDocs](https://environment-variables.readthedocs.io/en/latest/)

## Requirements

This package supports Python 3.7 or later

## Installation

Install using ``pip``:

```shell
$ pip install environment-variables
```

## Usage

Define your environment variables as class attributes with type annotation:

```python
from environment_variables import environment_variables


@environment_variables
class Environment:
    MY_VARIABLE: str
    MY_INTEGER: int = 10
    MY_FEATURE_FLAG: bool = False
```

When accessing a class attribute, the class will automatically check
the system for a environment variable of the same name and return
its value cast to the annotated type. If it is not defined, the default
value will be used instead.

It is also possible to annotate a class attribute with any class
using the `variables` function:

```python
from environment_variables import environment_variables, variable


@environment_variables
class Environment:
    MY_VARIABLE: CustomClass = variable(
        CustomClass,
        default='some default value',
        default_factory=custom_class_factory,
        args=(1, 2, 3,),
        kwargs={'more_custom': True},
    )
```



## The problem this is trying to solve

When configuring a python program with environment variables, one would
typically access them in a fashion similar to this:

```python
import os

my_value = os.getenv('MY_VALUE', default=123)
```

This leaves a lot of strings lying around in the code, and it gets hard
to keep track on which values are being used and what variables are needed
to be set when. A better approach would be to collect everything in a
config file:

```python
import os

class MyConfig:
    @classmethod
    def get_my_value(cls, default):
        return os.getenv('MY_VALUE', default=default)
```

This makes it slightly easier to keep track of, but we are still using
strings that we have to keep track of. An even better approach would
be to use Enums:

```python
import os
import enum

class MyVariables(enum.Enum):
    MY_VALUE = 'MY_VALUE'

class MyConfig:
    @classmethod
    def get_my_value(cls, default):
        return os.getenv(MyVariables.MY_VALUE.value, default=default)
```

Much better, now we can just look at the enum to see what variables we have,
but there is a lot of boilerplate code. For instance, do we really have to
write out 'MY_VALUE' twice in the enum definition? It would be much more
convenient to have the 'MyVaribles' class understand that the attribute name
should be the environment variable to look for, instead of having to specify
the string name of the variable again.

On top of that, `os.getenv` always returns strings, so we would have to
take care of the type casting ourselves if we want to have server ports
as integers or feature flags as booleans.
