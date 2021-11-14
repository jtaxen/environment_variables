import dataclasses
import pathlib
import pytest

from src.environment_variables import environment_variables, variable
from src.environment_variables.exceptions import EnvironmentVariableTypeError


@dataclasses.dataclass
class CustomFieldsClass:
    name: str
    without_default: str
    with_default: str = 'default'


@dataclasses.dataclass
class BadFieldsClass:
    pass


@environment_variables
class NonPrimitiveAttributes:
    PATH_TO_FILE: pathlib.Path
    PATH_TO_DIR: pathlib.Path


@environment_variables
class AttributeWithoutDefault:
    STRING_VALUE: CustomFieldsClass = variable(
        CustomFieldsClass, kwargs={'without_default': 'no-default'}
    )


@environment_variables
class AttributeWithDefault:
    STRING_VALUE: CustomFieldsClass = variable(
        CustomFieldsClass,
        kwargs={'without_default': 'no-default', 'with_default': 'not-default'},
    )


@environment_variables
class AttributeWithDefaultNoAnnotation:
    STRING_VALUE = variable(
        CustomFieldsClass,
        kwargs={'without_default': 'no-default', 'with_default': 'not-default'},
    )


@environment_variables
class AttributeWithPositionalArgument:
    STRING_VALUE = variable(
        CustomFieldsClass, args=('no-default',), kwargs={'with_default': 'not-default'}
    )


@environment_variables
class AttributeWithDefaultForEnvVar:
    DOES_NOT_EXIST = variable(
        CustomFieldsClass,
        default='my-default',
        args=('no-default',),
        kwargs={'with_default': 'not-default'},
    )


def custom_fields_class_factory(argument):
    return CustomFieldsClass(
        name='static name', without_default=argument, with_default='default'
    )


@environment_variables
class DefaultFactoryWithSetVariable:
    STRING_VALUE = variable(
        CustomFieldsClass,
        default_factory=custom_fields_class_factory,
    )


@environment_variables
class DefaultFactoryWithoutSetVariable:
    DOES_NOT_EXIST = variable(
        CustomFieldsClass,
        default='default',
        default_factory=custom_fields_class_factory,
    )


def test_if_type_is_class_then_variable_is_used_to_init_the_class():
    assert isinstance(NonPrimitiveAttributes.PATH_TO_FILE, pathlib.Path)
    assert pathlib.Path('/path/to/some/file.txt') == NonPrimitiveAttributes.PATH_TO_FILE

    assert isinstance(NonPrimitiveAttributes.PATH_TO_DIR, pathlib.Path)
    assert pathlib.Path('/path/to/directory') == NonPrimitiveAttributes.PATH_TO_DIR


def test_cast_variable_to_custom_class_without_defaults():
    assert isinstance(AttributeWithoutDefault.STRING_VALUE, CustomFieldsClass)
    assert 'no-default' == AttributeWithoutDefault.STRING_VALUE.without_default
    assert 'default' == AttributeWithoutDefault.STRING_VALUE.with_default


@pytest.mark.parametrize(
    "env_var_class",
    [
        AttributeWithDefault,
        AttributeWithDefaultNoAnnotation,
        AttributeWithPositionalArgument,
    ],
)
def test_cast_variable_to_custom_class_with_defaults(env_var_class):
    assert isinstance(env_var_class.STRING_VALUE, CustomFieldsClass)
    assert 'no-default' == env_var_class.STRING_VALUE.without_default
    assert 'not-default' == env_var_class.STRING_VALUE.with_default


def test_annotation_must_match_variable_class():
    # Given
    class ConflictingAnnotations:
        STRING_VALUE: BadFieldsClass = variable(
            CustomFieldsClass,
            kwargs={'without_default': 'no-default', 'with_default': 'not-default'},
        )

    # Then
    with pytest.raises(EnvironmentVariableTypeError):
        # When
        environment_variables(ConflictingAnnotations)


def test_default_value_is_passed_to_class_constructor():
    assert isinstance(AttributeWithDefaultForEnvVar.DOES_NOT_EXIST, CustomFieldsClass)
    assert 'my-default' == AttributeWithDefaultForEnvVar.DOES_NOT_EXIST.name
    assert 'no-default' == AttributeWithDefaultForEnvVar.DOES_NOT_EXIST.without_default
    assert 'not-default' == AttributeWithDefaultForEnvVar.DOES_NOT_EXIST.with_default


def test_default_factory_returns_instance_with_environment_argument_if_set():
    assert isinstance(DefaultFactoryWithSetVariable.STRING_VALUE, CustomFieldsClass)
    assert 'static name' == DefaultFactoryWithSetVariable.STRING_VALUE.name
    assert 'string value' == DefaultFactoryWithSetVariable.STRING_VALUE.without_default
    assert 'default' == DefaultFactoryWithSetVariable.STRING_VALUE.with_default


def test_default_factory_uses_default_value_if_environment_variable_is_not_set():
    assert isinstance(
        DefaultFactoryWithoutSetVariable.DOES_NOT_EXIST, CustomFieldsClass
    )
    assert 'static name' == DefaultFactoryWithoutSetVariable.DOES_NOT_EXIST.name
    assert 'default' == DefaultFactoryWithoutSetVariable.DOES_NOT_EXIST.without_default
    assert 'default' == DefaultFactoryWithoutSetVariable.DOES_NOT_EXIST.with_default
