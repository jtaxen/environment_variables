import dataclasses
import pathlib
import pytest

from src.environment_variables import environment_variables, variable


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
        CustomFieldsClass, without_default='no-default'
    )


@environment_variables
class AttributeWithDefault:
    STRING_VALUE: CustomFieldsClass = variable(
        CustomFieldsClass, without_default='no-default', with_default='not-default'
    )


@environment_variables
class AttributeWithDefaultNoAnnotation:
    STRING_VALUE = variable(
        CustomFieldsClass, without_default='no-default', with_default='not-default'
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
    "env_var_class", [AttributeWithDefault, AttributeWithDefaultNoAnnotation]
)
def test_cast_variable_to_custom_class_with_defaults(env_var_class):
    assert isinstance(env_var_class.STRING_VALUE, CustomFieldsClass)
    assert 'no-default' == env_var_class.STRING_VALUE.without_default
    assert 'not-default' == env_var_class.STRING_VALUE.with_default


def test_annotation_must_match_variable_class():
    # Given
    class ConflictingAnnotations:
        STRING_VALUE: BadFieldsClass = variable(
            CustomFieldsClass, without_default='no-default', with_default='not-default'
        )

    # Then
    with pytest.raises(ValueError):
        # When
        environment_variables(ConflictingAnnotations)
