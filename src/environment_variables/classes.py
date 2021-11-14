import os

from .variables import Variable, _VariableTemplate
from .exceptions import (
    EnvironmentValidationError,
    EnvironmentVariableNotSetError,
    EnvironmentVariableTypeError,
)


def _validate_environment_variables(cls):
    """Run through all environment variables set in this class and make
    sure that they are all either defined on a system level, or have a
    default set. Also check that the variables are castable to the
    desired type.

    :raises EnvironmentValidationError: if any variable fails the
    validation criteria. The error contains information on all the
    attributes that have failed the validation
    """
    message = ''
    for name, attribute in cls.__dict__.items():
        if isinstance(attribute, Variable):
            try:
                _ = attribute.value
            except EnvironmentVariableNotSetError:
                message += (
                    f"Environment variable '{name}' has not been set and "
                    "has no default value\n"
                )
            except EnvironmentVariableTypeError:
                message += (
                    f"Environment variable '{name}' can not be cast to "
                    f"type '{attribute.type}'\n"
                )

    if message:
        raise EnvironmentValidationError(message)


def _add_variables_by_prefix(cls, prefix):
    variables = {
        key: value for key, value in os.environ.items() if key.startswith(prefix)
    }
    for key, value in variables.items():
        if not hasattr(cls, key):
            setattr(cls, key, Variable(key=key, type_=str))


class EnvVarMeta(type):
    """Metaclass for creating EnvVars classes. Environment variable
    classes can be created by using this metaclass, but the recommended
    way is to use the `@environment_variables` wrapper.
    """

    def __new__(mcs, name, bases, dictionary):
        """When creating a new EnvVars class, capture the
        set attributes of the class and add entries in the
        class.__dict__, where each attribute is stored as
        a Variable object.
        """
        cls = super().__new__(mcs, name, bases, dictionary)

        variables = {}

        # First, look in __annotations__ to see if there are
        # anny fields there that need to be captured. These
        # attributes will only have a name and a type annotation
        for key, value in dictionary.get('__annotations__', {}).items():
            variables[key] = Variable(key=key, type_=value)

        # Look in the dictionary for all attributes that have
        # do not start with __. These attributes will contain
        # defaults if they exist.
        variables_with_default = {
            key: value for key, value in dictionary.items() if not key.startswith('__')
        }

        # Update the captured variables with their default
        # value, if any such value is present, and the annotated
        # type.
        variables = {
            key: Variable(
                key=key, type_=value.type, default=variables_with_default.pop(key, None)
            )
            for key, value in variables.items()
        }

        # If any variables are left, add them as well, and
        # infer the type from the given default.
        variables.update(
            {
                key: Variable(
                    key=key,
                    type_=value.class_or_type
                    if isinstance(value, _VariableTemplate)
                    else type(value),
                    default=value,
                )
                for key, value in variables_with_default.items()
            }
        )

        for key, value in variables.items():
            setattr(cls, key, value)

        setattr(cls, 'validate', classmethod(_validate_environment_variables))
        setattr(cls, 'add_variables_by_prefix', classmethod(_add_variables_by_prefix))

        return cls

    def __getattribute__(self, item):
        """Override __getattribute__ to return the variable
        value if the item is an instance of a variable.
        """
        attribute = super().__getattribute__(item)
        if isinstance(attribute, Variable):
            return attribute.value

        return attribute


class EnvVars(metaclass=EnvVarMeta):
    """Base class using the EnvVarMeta metaclass. Subclassing this class
    is equivalent to wrapping the class with the `environment_variables`
    function.
    """


def environment_variables(cls=None, *, validate=False, collect_prefixes=None):
    """Create an EnvVar class from the provided `cls`. This function can
    be used to wrap a class:

    .. code-block:: python

        @environment_variables
        class Environment:
            MY_VARIABLE: str

    or:

    .. code-block:: python

        @environment_variables(validate=True, collect_prefixes=['ZSH'])
        class Environment:
            pass

    :param cls: the class definition to use
    :param validate: if True, run through all environment variables
    and raise an error if any variable is not set nor have a default
    :param collect_prefixes: if a list of prefixes is provided, the
    class will automatically add environment variables with those
    prefixes. This might be useful to get a quick access when debugging
    or experimenting, but it will dynamically add different environment
    variables depending on how the system is set up, while also
    obscuring what variables are being used, and is not recommended in
    a project where code is shared between several developers.
    """
    if collect_prefixes is None:
        collect_prefixes = []

    def wrap(old_cls):
        name = str(old_cls.__name__)
        bases = tuple(old_cls.__bases__)
        class_dict = dict(old_cls.__dict__)

        new_cls = EnvVarMeta(name, bases, class_dict)

        for prefix in collect_prefixes:
            new_cls.add_variables_by_prefix(prefix)

        if validate:
            new_cls.validate()

        return new_cls

    if cls is None:
        return wrap

    return wrap(cls)
