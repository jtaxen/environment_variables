"""This package lets you define enum-style classes to access your
environment variables, with type annotation and optional default
values. The most straight-forward way of defining your class is to wrap
it with the :ref `environment_variable <environment-varables-wrapper>`
function:

.. code-block:: python

    from environment_variables import environment_variables

    @environment_variables
    class Environment:
        MY_VARIABLE: str
        MY_INTEGER: int
        MY_FEATURE_FLAG: bool = False

When you access the class attributes, the class will automatically check
your system for an environment variable of the same name and return its
value cast to the annotated type. If the environment variable is not set
but a default value has been set, that default value will be returned
instead.

>>> class Environment:
...     MY_VARIABLE: str = 'some default string'
...
>>> Environment.MY_VARIABLE
'some system string'

If an environment variable is not set, and the class attribute does not
have a default value, then an `EnvironmentVariableError` will be raised.
"""
from .classes import EnvVarMeta, EnvVars, environment_variables
from .variables import variable
