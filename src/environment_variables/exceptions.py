"""Environment variable exceptions"""


class EnvironmentVariableError(Exception):
    pass


class EnvironmentValidationError(EnvironmentVariableError):
    """Raised when the validation of an environment variable class has
    failed, either because the class has an attribute whose type
    annotation does not match its provided default value, or because
    the attribute has no default and the corresponding environment
    variable is not set on the system
    """


class EnvironmentVariableNotSetError(EnvironmentVariableError):
    """Raised when trying to access the value of an environment variable
    that has not been set on the system, and has no default defined
    """


class EnvironmentVariableTypeError(EnvironmentVariableError):
    """Raised if the value of an environment variable cannot be cast to
    the desired type, or if the annotated type or class does not match
    the type or class of the provided default value, or any other
    occasion when values and types do not match
    """
