import pytest
from attack import main
from moto import mock_resourcegroupstaggingapi

def test_create_iam_role(iam_client):
    roleName = "test-role"
    newRole = main.create_iam_role_for_lambda(iam_client, roleName)
    assert newRole['Role']['RoleName'] == roleName, "New role created!"

def test_create_lambda_function(lambda_client, iam_client):
    functionName = "test-function"
    newfunction = main.create_function(
        lambda_client, functionName, "test_handler", "test_package.zip", 
        main.create_iam_role_for_lambda(iam_client, "test-role")
    )
    assert functionName in newfunction, "Function created!"

@mock_resourcegroupstaggingapi
def test_get_resources(s3_client):
    regions = ["us-east-1", "us-west-2", "eu-central-1", "ap-southeast-1", "ca-central-1"]
    gatheredData = main.get_all_resources(s3_client, regions)
    
    assert type(gatheredData) is list, "Gathered data is a list"
    # Check for S3 and region in the gathered data
    for data in gatheredData:
        assert 'region' or 'S3' in data, "S3 and regions exist in the response)"
        assert type(data) is dict, "Data response is a dictionary"

def test_get_security_groups(ec2_client):
    securityGroups = main.get_security_groups(ec2_client)

    # Check for default security group in the list, this group will always exist
    for group in securityGroups:
        assert "default" in group['name']
        assert 'sg-' in group['id']
