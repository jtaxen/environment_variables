import dataclasses
import os
import typing


@dataclasses.dataclass
class Variable:
    """Representation of an environment variable.
    @param key: Name of the environment variable.
    @param type: Type to cast the environment variable to
    after loading its value.
    @param default: Optional default of the value, if it
    is not defined on the system. If a default
    is not set, and the environment variable is
    not defined on the system, an AttributeError
    is raised when trying to access the variable.
    """
    key: str
    type: type
    default: typing.Optional[typing.Any] = None
    _value: typing.Any = None

    def __post_init__(self):
        """After initialisation, make sure that the provided
        default is of the same type as the expected type.
        """
        if self.default is not None and type(self.default) != self.type:
            raise ValueError(
                f"The default value '{self.default}' is not of type '{self.type}'"
            )

    @property
    def value(self):
        """Access the value of the environment variable.

        :return: The value of the environment variable, cast
        to the desired type, or, if the environment variable
        is not defined, return the default value
        :raises AttributeError: if the environment variable
        is not set and there is no default value to fall
        back on
        :raises ValueError: if the environment variable
        cannot be cast to the desired type
        """
        if self._value:
            return self._value

        raw_value = os.getenv(self.key, default=self.default)

        if raw_value is None:
            raise AttributeError(
                f"The environment variable '{self.key}' is not set and no default "
                "has been provided"
            )

        if self.type == bool:
            # If the raw value is a boolean, that means that
            # the environment variable was not set, and that
            # we fell back on the default value, which already
            # is a boolean
            if isinstance(raw_value, bool):
                return raw_value

            if raw_value.isdigit():
                return bool(int(raw_value))

            if raw_value.lower() not in ['true', 'false']:
                raise ValueError(
                    f"The value '{raw_value}' can not be cast to 'boolean'"
                )

            # Return true if we have the string 'true' and
            # false if we have the string 'false'
            return raw_value.lower() == 'true'

        # Cast the raw value to our desired type
        try:
            self._value = self.type(raw_value)
        except ValueError as error:
            raise ValueError(
                f"Error reading environment variable '{self.key}': cannot cast"
                f"value '{raw_value}' to type '{self.type}'"
            ) from error

        return self._value
