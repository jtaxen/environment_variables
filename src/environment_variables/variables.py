import dataclasses
import os
import typing

from .exceptions import EnvironmentVariableNotSetError, EnvironmentVariableTypeError


@dataclasses.dataclass(frozen=True)
class _VariableTemplate:
    class_or_type: typing.Union[typing.Callable, type]
    default: str = None
    default_factory: typing.Callable = None
    args: tuple = None
    kwargs: dict = None


class Variable:
    def __init__(
        self,
        key: str,
        type_: typing.Union[typing.Type, _VariableTemplate],
        default: typing.Optional[typing.Any] = None,
    ):
        """Representation of an environment variable.

        :param key: Name of the environment variable.
        :param type: Type to cast the environment variable to after
        loading its value.
        :param default: Optional default of the value, if it is not
        defined on the system.
        """
        self.key = key
        self._type = type_
        self.default = default
        self._value = None
        self._args = None
        self._kwargs = None
        self._template_default = None
        self._default_factory = None

        if isinstance(self.default, _VariableTemplate):
            if self._type is not None and self._type != self.default.class_or_type:
                raise EnvironmentVariableTypeError(
                    f"The default value '{self.default.class_or_type}' is not of type '"
                    f"{self._type}'"
                )

            self._args = self.default.args
            self._kwargs = self.default.kwargs
            self._type = self.default.class_or_type
            self._template_default = self.default.default
            self._default_factory = self.default.default_factory
            self.default = None

        if self.default is not None and type(self.default) != self._type:
            raise EnvironmentVariableTypeError(
                f"The default value '{self.default}' is not of type '{self._type}'"
            )

    @property
    def value(self):
        """Access the value of the environment variable.

        :return: The value of the environment variable, cast
        to the desired type, or, if the environment variable
        is not defined, return the default value
        :raises EnvironmentVariableNotSetError: if the environment variable
        is not set and there is no default value to fall
        back on
        :raises EnvironmentVariableTypeError: if the environment variable
        cannot be cast to the desired type
        """
        if self._value:
            return self._value

        default = self.default if self.default is not None else self._template_default
        raw_value = os.getenv(self.key, default=default)

        if raw_value is None:
            raise EnvironmentVariableNotSetError(
                f"The environment variable '{self.key}' is not set and no default "
                "has been provided"
            )

        if self._default_factory:
            return self._default_factory(raw_value)

        if self._args or self._kwargs:
            return self.type(raw_value, *self._args, **self._kwargs)

        if self._type == bool:
            # If the raw value is a boolean, that means that
            # the environment variable was not set, and that
            # we fell back on the default value, which already
            # is a boolean
            if isinstance(raw_value, bool):
                return raw_value

            if raw_value in ['0', '1']:
                return bool(int(raw_value))

            if raw_value.lower() not in ['true', 'false']:
                raise EnvironmentVariableTypeError(
                    f"The value '{raw_value}' can not be cast to 'boolean'"
                )

            # Return true if we have the string 'true' and
            # false if we have the string 'false'
            return raw_value.lower() == 'true'

        # Cast the raw value to our desired type
        try:
            self._value = self.type(raw_value)
        except ValueError as error:
            raise EnvironmentVariableTypeError(
                f"Error reading environment variable '{self.key}': cannot cast"
                f"value '{raw_value}' to type '{self._type}'"
            ) from error

        return self._value

    @property
    def type(self):
        if isinstance(self._type, _VariableTemplate):
            return self._type.class_or_type

        return self._type


def variable(class_or_type, default=None, default_factory=None, args=None, kwargs=None):
    """Create an attribute that is of a class or type that has more
    arguments than one, and pass the extra arguments to its initializer.

    The init function of :class_or_type: will be called with the value
    of the environment variable as the first argument, and then with
    any additional :args: and :kwargs:

    :param class_or_type: class or type of this attribute
    :param default: default string value to be passed to the class
    constructor of `class_or_type`
    :param args: additional arguments that will be passed directly to
    the :class_or_type: constructor
    :param kwargs: additional keyword arguments that wil be passed
    directly to the constructor
    """
    args = args or tuple()
    kwargs = kwargs or dict()

    return _VariableTemplate(
        class_or_type,
        default=default,
        default_factory=default_factory,
        args=args,
        kwargs=kwargs,
    )
