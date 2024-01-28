import json

from pytest import fixture

from ocrd_validators import OcrdResourceListValidator
from tests.base import (  # pylint: disable=import-error,no-name-in-module
    TestCase, main)


@fixture
def reslist():
    return {
        'ocrd-foo': [
            {
                'url': 'https:/foo',
                'type': 'file',
                'size': 123,
                'description': 'something descriptive',
                'name': 'foo',
                'version_range': '>= 0.0.1'
            }
        ]
    }

def test_resource_list_validator(reslist):
    report = OcrdResourceListValidator.validate(reslist)
    print(report.errors)
    assert report.is_valid == True

if __name__ == '__main__':
    main(__file__)
