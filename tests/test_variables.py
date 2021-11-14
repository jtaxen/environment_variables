import os
import itertools

import pytest

from src.environment_variables.variables import Variable, _VariableTemplate
from src.environment_variables.exceptions import (
    EnvironmentVariableNotSetError,
    EnvironmentVariableTypeError,
)


def test_variable_without_default_returns_value(environment_variables):
    # Given
    variable = Variable(key='STRING_VALUE', type_=str)

    # When
    value = variable.value

    # Then
    assert environment_variables.get('STRING_VALUE') == value
    assert isinstance(value, str)


def test_variable_with_default_returns_existing_value(environment_variables):
    # Given
    variable = Variable(key='STRING_VALUE', type_=str, default='DEFAULT')

    # When
    value = variable.value

    # Then
    assert environment_variables.get('STRING_VALUE') == value
    assert isinstance(value, str)


def test_variable_with_default_returns_default_if_env_var_is_undefined():
    # Given
    variable = Variable(key='DOES_NOT_EXIST', type_=str, default='DEFAULT')

    # When
    value = variable.value

    # Then
    assert 'DEFAULT' == value
    assert isinstance(value, str)


def test_variable_without_default_raises_error_if_env_var_is_undefined():
    # Given
    variable = Variable(key='DOES_NOT_EXIST', type_=str)

    # Then
    with pytest.raises(EnvironmentVariableNotSetError):
        # When
        _ = variable.value


@pytest.mark.parametrize(
    "default,variable_type",
    list(
        itertools.product(['STRING', True, False, 10, 11.01], [str, bool, int, float])
    ),
)
def test_variable_default_must_match_given_type_annotation(default, variable_type):
    if type(default) == variable_type:
        try:
            _ = Variable('SOME_KEY', type_=variable_type, default=default)
        except EnvironmentVariableTypeError:
            pytest.fail()

    else:
        with pytest.raises(EnvironmentVariableTypeError):
            _ = Variable('SOME_KEY', type_=variable_type, default=default)


def test_if_attribute_is_defined_as_variable_template_then_variable_type_matches():
    # Given
    class SomeClass:
        pass

    variable_template = _VariableTemplate(
        class_or_type=SomeClass,
    )

    variable = Variable(
        key='key',
        type_=variable_template,
    )

    # Then
    assert SomeClass == variable.type


@pytest.mark.parametrize(
    'boolean_representation', ['truth', 'YES', 'falsely', 'NO', '2', '-1', '0.0']
)
def test_casting_non_boolean_value_to_boolean_raises_error(boolean_representation):
    # Given
    os.environ['SOME_KEY'] = boolean_representation
    variable = Variable('SOME_KEY', type_=bool)

    # Then
    with pytest.raises(EnvironmentVariableTypeError):
        # When
        _ = variable.value
