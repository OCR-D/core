import json

from tests.base import TestCase, main # pylint: disable=import-error,no-name-in-module
from pytest import fixture

from ocrd_validators import OcrdResourceListValidator

@fixture
def reslist():
    return {
        'ocrd-foo': [
            {
                'url': 'https:/foo',
                'type': 'direct-link',
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
