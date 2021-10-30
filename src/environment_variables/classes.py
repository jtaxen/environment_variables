import os

from .variables import Variable


def validate_environment_variables(cls):
    """Run through all environment variables set in this class
    and make sure that they all are either defined or have a
    default set. Also check that the variables are castable
    to the desired type.
    """
    message = ''
    for name, attribute in cls.__dict__.items():
        if isinstance(attribute, Variable):
            try:
                _ = attribute.value
            except AttributeError:
                message += (
                    f"Environment variable '{name}' has not been set and "
                    "has no default value\n"
                )
            except ValueError:
                message += (
                    f"Environment variable '{name}' can not be cast to "
                    f"type '{attribute.type}'\n"
                )

    if message:
        raise ValueError(message)

def add_variables_by_prefix(cls, prefix):
    variables = {
        key: value for key, value in os.environ.items() if key.startswith(prefix)
    }
    for key, value in variables.items():
        if not hasattr(cls, key):
            setattr(cls, key, Variable(key=key, type=str))




class EnvVarMeta(type):
    """Metaclass for creating EnvVars classes.
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
            variables[key] = Variable(key=key, type=value)

        # Look in the dictionary for all attributes that have
        # do not start with __. These attributes will contain
        # defaults if they exist.
        variables_with_default = {
            key: value for key, value in dictionary.items()
            if not key.startswith('__')
        }

        # Update the captured variables with their default
        # value, if any such value is present, and the annotated
        # type.
        variables = {
            key: Variable(
                key=key,
                type=value.type,
                default=variables_with_default.pop(key, None)
            ) for key, value in variables.items()
        }

        # If any variables are left, add them as well, and
        # infer the type from the given default.
        variables.update(
            {
                key: Variable(
                    key=key,
                    type=type(value),
                    default=value,
                ) for key, value in variables_with_default.items()
            }
        )

        for key, value in variables.items():
            setattr(cls, key, value)

        setattr(cls, 'validate', classmethod(validate_environment_variables))
        setattr(cls, 'add_variables_by_prefix', classmethod(add_variables_by_prefix))

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
    pass


def environment_variables(cls=None, /, *, validate=False, prefixes=[]):
    """
    :param cls: Class to cast to EnvVars class
    :param validate: if True, run through all environment variables
    and raise an error if any variable is not set nor have a default
    :param prefixes: if a list of prefixes is provided, the class
    will automatically add environment variables with those prefixes
    """
    def wrap(old_cls):
        name = str(old_cls.__name__)
        bases = tuple(old_cls.__bases__)
        class_dict = dict(old_cls.__dict__)

        new_cls = EnvVarMeta(name, bases, class_dict)
        if prefixes:
            for prefix in prefixes:
                new_cls.add_variables_by_prefix(prefix)

        if validate:
            new_cls.validate()

        return new_cls

    if cls is None:
        return wrap

    return wrap(cls)
