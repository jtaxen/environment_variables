Usage
=====


Defining a class
----------------

There are four ways of defining an environment variable class. The recommended way is
to use the ``environment_variables`` function as a wrapper:

.. code-block:: python

    from environment_variables import environment_variables

    @environment_variables
    class Environment:
        MY_VARIABLE: str

but these can also be defined by choosing the metaclass ``EnvVarsMeta``:

.. code-block:: python

    from environment_variables import EnvVarsMeta

    class Environment(metaclass=EnvVarsMeta)
        MY_VARIABLE: str

as a subclass of the ``EnvVars`` class:

.. code-block:: python

    from environment_variables import EnvVars

    class Environment(EnvVars):
        MY_VARIABLE: str

or by using the ``environment_variables`` function as a regular function:

.. code-block:: python

    from environment_variables import environment_variables

    class Environment:
        MY_VARIABLE: str

    environment = environment_variables(Environment)


Type annotations
----------------

Using type annotations, you can define what type you want your environment variable to
be cast to. Casting to ``str``, ``int``, ``float`` and ``bool`` are trivial, but you can also
define simple classes whose init functions only need one positional argument. In this
case, the loaded value will be passed directly as a string to the init method as the
first positional argument.

.. code-block:: python

    import pathlib
    from environment_variables import environment_variables

    @environment_variables
    class Environment:
        MY_STRING: str
        MY_INTEGER: int
        MY_FLOAT: float
        MY_BOOL: bool
        MY_PATH: pathlib.Path

In the above example, if an environment variable is defined as ``MY_PATH=/path/to/resource``,
then the attribute ``Environment.MY_PATH`` will be whatever ``pathlib.Path('/path/to/resource')``
evaluates to. To annotate classes that require more than one argument, see :ref:`variable-function`.


Defaults
--------

Default values for variables can be set by assigning a value to an attribute:

.. code-block:: python

    from environment_variables import environment_variables

    @environment_variables
    class Environment:
        MY_STRING: str = 'default string'
        MY_INTEGER: int = 123

If the environment variable is not defined on the system, the default value will be
returned instead. If a default value is provided, the type annotation is not even
necessary, since the type of the variable will be inferred from the type of the
default. If you define your class like

.. code-block:: python

    from environment_variables import environment_variables

    @environment_variables
    class Environment:
        MY_INTEGER = 123
        MY_BOOL = False

then ``MY_INTEGER`` will be an integer and ``MY_BOOL`` a boolean, regardless of the
corresponding environment variables are set or not. A Python developer should not
have to worry about types if it is not necessary.


.. _variable-function:

Variable fields
---------------

In some cases, a type annotation is not enough to define how an attribute should behave.
In that case, you can use the ``variable`` function to define how you want your
attribute to be created.

.. code-block:: python

    from environment_variables import environment_variables, variable

    @environment_variables
    class Environment:
        MY_ATTRIBUTE = variable(
            MyClass,
            default='default',
            args=('some argument',),
            kwargs={'key': 'value'}
        )

This method sets ``MY_ATTRIBUTE`` to an instance of ``MyClass``, with the first
argument passed to the ``MyClass`` init method being either the value of the environment
variable ``MY_ATTRIBUTE`` if it is set, or ``default`` if the variable is not set. The
arguments ``args`` and ``kwargs`` are used as further arguments to the init method.

If needed, i.e. if the environment variable is not the first argument to the constructor,
a factory method can be provided:

.. code-block:: python

    from environment_variables import environment_variables, variable

    @environment_variables
    class Environment:
        MY_ATTRIBUTE = variable(
            MyClass,
            default='default'
            default_factory: create_my_class
        )

This function should take the value of the environment variable or the value of ``default``
as its only argument and return an instance of ``MyClass`` and can initialize it in
whatever way is desired.
