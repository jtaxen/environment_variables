import itertools

import pytest

from src.environment_variables.variables import Variable


def test_variable_without_default_returns_value(environment_variables):
    # Given
    variable = Variable(key='STRING_VALUE', type=str)

    # When
    value = variable.value

    # Then
    assert environment_variables.get('STRING_VALUE') == value
    assert isinstance(value, str)


def test_variable_with_default_returns_existing_value(environment_variables):
    # Given
    variable = Variable(key='STRING_VALUE', type=str, default='DEFAULT')

    # When
    value = variable.value

    # Then
    assert environment_variables.get('STRING_VALUE') == value
    assert isinstance(value, str)


def test_variable_with_default_returns_default_if_env_var_is_undefined():
    # Given
    variable = Variable(key='DOES_NOT_EXIST', type=str, default='DEFAULT')

    # When
    value = variable.value

    # Then
    assert 'DEFAULT' == value
    assert isinstance(value, str)


def test_variable_without_default_raises_error_if_env_var_is_undefined():
    # Given
    variable = Variable(key='DOES_NOT_EXIST', type=str)

    # Then
    with pytest.raises(AttributeError):
        # When
        value = variable.value


@pytest.mark.parametrize(
    "default,variable_type",
    list(itertools.product(
        ['STRING', True, False, 10, 11.01],
        [str, bool, int, float]
    ))
)
def test_variable_default_must_match_given_type_annotation(default, variable_type):
    if type(default) == variable_type:
        try:
            _ = Variable('SOME_KEY', type=variable_type, default=default)
        except ValueError:
            pytest.fail()

    else:
        with pytest.raises(ValueError):
            _ = Variable('SOME_KEY', type=variable_type, default=default)