import pytest

from src.environment_variables import environment_variables


@environment_variables
class EnvironmentWithDefaults:
    DEFINED_BOOLEAN_TRUE: bool = False
    DEFINED_BOOLEAN_FALSE: bool = True
    DEFINED_STRING_VALUE: str = 'DEFAULT'
    DEFINED_FLOAT_VALUE: float = 12.0
    DEFINED_INTEGER_VALUE: int = 12
    UNDEFINED_BOOLEAN_TRUE: bool = True
    UNDEFINED_BOOLEAN_FALSE: bool = False
    UNDEFINED_STRING_VALUE: str = 'DEFAULT'
    UNDEFINED_FLOAT_VALUE: float = 14.0
    UNDEFINED_INTEGER_VALUE: int = 14


def test_defined_boolean_true_takes_precedence_over_default():
    assert EnvironmentWithDefaults.DEFINED_BOOLEAN_TRUE
    assert isinstance(EnvironmentWithDefaults.DEFINED_BOOLEAN_TRUE, bool)


def test_defined_boolean_false_takes_precedence_over_default():
    assert not EnvironmentWithDefaults.DEFINED_BOOLEAN_FALSE
    assert isinstance(EnvironmentWithDefaults.DEFINED_BOOLEAN_FALSE, bool)


def test_defined_string_takes_precedence_over_default():
    assert 'STRING_VALUE' == EnvironmentWithDefaults.DEFINED_STRING_VALUE
    assert isinstance(EnvironmentWithDefaults.DEFINED_STRING_VALUE, str)


def test_defined_float_takes_precedence_over_default():
    assert 10.001 == EnvironmentWithDefaults.DEFINED_FLOAT_VALUE
    assert isinstance(EnvironmentWithDefaults.DEFINED_FLOAT_VALUE, float)


def test_defined_int_takes_precedence_over_default():
    assert 19 == EnvironmentWithDefaults.DEFINED_INTEGER_VALUE
    assert isinstance(EnvironmentWithDefaults.DEFINED_INTEGER_VALUE, int)


def test_undefined_boolean_true_is_replaced_with_default():
    assert EnvironmentWithDefaults.UNDEFINED_BOOLEAN_TRUE
    assert isinstance(EnvironmentWithDefaults.UNDEFINED_BOOLEAN_TRUE, bool)


def test_undefined_boolean_false_is_replaced_with_default():
    assert not EnvironmentWithDefaults.UNDEFINED_BOOLEAN_FALSE
    assert isinstance(EnvironmentWithDefaults.UNDEFINED_BOOLEAN_FALSE, bool)


def test_defined_string_is_replaced_with_default():
    assert 'DEFAULT' == EnvironmentWithDefaults.UNDEFINED_STRING_VALUE
    assert isinstance(EnvironmentWithDefaults.UNDEFINED_STRING_VALUE, str)


def test_defined_float_is_replaced_with_default():
    assert 14.0 == EnvironmentWithDefaults.UNDEFINED_FLOAT_VALUE
    assert isinstance(EnvironmentWithDefaults.UNDEFINED_FLOAT_VALUE, float)


def test_defined_int_is_replaced_with_default():
    assert 14 == EnvironmentWithDefaults.UNDEFINED_INTEGER_VALUE
    assert isinstance(EnvironmentWithDefaults.UNDEFINED_INTEGER_VALUE, int)


@pytest.mark.parametrize(
    'default',
    ['STRING', 10, 10.1, True, False]
)
def test_default_with_missing_annotation_can_be_inferred(default):
    class WithMissingAnnotation:
        VARIABLE = default

    env_class = environment_variables(WithMissingAnnotation)

    assert default == env_class.VARIABLE
    assert isinstance(env_class.VARIABLE, type(default))


def test_default_with_missing_annotation_returns_correct_env_var_if_defined():
    class WithMissingAnnotation:
        BOOLEAN_TRUE = False
        BOOLEAN_FALSE = True
        STRING_VALUE = 'DEFAULT'
        FLOAT_VALUE = 5.5
        INTEGER_VALUE = 7

    env_class = environment_variables(WithMissingAnnotation)

    assert isinstance(env_class.BOOLEAN_TRUE, bool)
    assert env_class.BOOLEAN_TRUE
    assert isinstance(env_class.BOOLEAN_FALSE, bool)
    assert not env_class.BOOLEAN_FALSE
    assert isinstance(env_class.STRING_VALUE, str)
    assert '/path/to/some/place' == env_class.STRING_VALUE
    assert isinstance(env_class.FLOAT_VALUE, float)
    assert 10.001 == env_class.FLOAT_VALUE
    assert isinstance(env_class.INTEGER_VALUE, int)
    assert 19 == env_class.INTEGER_VALUE
