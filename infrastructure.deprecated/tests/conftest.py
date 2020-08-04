import os
import pytest
import json
import boto3

FIXTURE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files','galileoBabelNotification.json',
    )

def pytest_addoption(parser):
    parser.addoption("--resource", action="append", default=[], help="list of stringinputs to pass to test functions")

def pytest_generate_tests(metafunc):
    if 'resource' in metafunc.fixturenames:
        metafunc.parametrize("resource",
                             metafunc.config.getoption('resource'))

@pytest.fixture(scope="module")
def data():
    return json.load(open(FIXTURE_PATH))

@pytest.fixture(scope="module")
def aws_lambda():
    return boto3.client('lambda', region_name="eu-west-2")

@pytest.fixture(scope="module")
def s3():
    return boto3.resource('s3', region_name="eu-west-2")
    