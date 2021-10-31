# Environment variables

![pytest](https://github.com/jtaxen/environment_variables/actions/workflows/pytest.yml/badge.svg)
[![pypi](https://img.shields.io/pypi/v/environment_variables.svg)](https://pypi.python.org/project/environment_variables)
[![license](https://img.shields.io/github/license/jtaxen/environment_variables.svg)](https://github.com/jtaxen/environment_variables/blob/main/LICENSE)

Enum style access to environment variables with type annotations

~ Av var och env efter förmåga
  åt var och env efter behov ~

## Requirements

This package supports Python 3.7 or later


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

The `environment_variables` function has several arguments:

```python
from environment_variables import environment_variables


@environment_variables(validate=True, prefixes=['FLASK_APP', 'ZSH'])
class Environment:
    MY_VARIABLE: str
    MY_INTEGER: int = 10
    MY_FEATURE_FLAG: bool = False
```

If `validate` is `True`, a validation will be made when the class is
loaded, that will check if all the attributes either are defined in
the environment, or that they have been provided with a default. If
not, a `ValueError` is raised.

If `prefixes` is provided, the class will search through the environment
for variables whose prefixes match the given ones and automatically
add them as attributes to the class. You can then use them like

```shell
>>>> class Environment: pass
>>>> environment = environment_variables(Environment, prefixes=['TERM'])
>>>> environment.TERM
'screen-256color'
>>>> environment.TERM_PROGRAM
'tmux'
```

It is also possible to annotate a class attribute with any class
using the `variables` function:

```python
from environment_variables import environment_variables, variable


@environment_variables
class Environment:
    MY_VARIABLE: CustomClass = variable(
        CustomClass,
        'argument',
        keyword='other_arguent'
    )
```

The environment variable is then used as the first argument to the class
constructor, followed by any args and kwargs passed to the variable
function.


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

