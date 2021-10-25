import os
import pytest
import unittest.mock


@pytest.fixture(scope='module', autouse=True)
def environment_variables():
    return {
        'BOOLEAN_TRUE': 'true',
        'BOOLEAN_FALSE': 'false',
        'BOOLEAN_TRUE_AS_INT': '1',
        'BOOLEAN_FALSE_AS_INT': '0',
        'STRING_VALUE': '/path/to/some/place',
        'FLOAT_VALUE': '10.001',
        'INTEGER_VALUE': '19',
        'DEFINED_BOOLEAN_TRUE': 'true',
        'DEFINED_BOOLEAN_FALSE': 'false',
        'DEFINED_STRING_VALUE': 'STRING_VALUE',
        'DEFINED_FLOAT_VALUE': '10.001',
        'DEFINED_INTEGER_VALUE': '19',
    }


@pytest.fixture(scope='module', autouse=True)
def fake_environment(environment_variables):
    with unittest.mock.patch.dict(os.environ, environment_variables):
        yield
