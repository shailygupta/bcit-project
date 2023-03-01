# BCIT project COMP 8045

## Pre-requisites
To run the worm on a local machine the following prerequisites are required:

- Terraform (latest version) + basic terraform knowledge
- Python version 3.9 
- AWS account (a singular account can be used for testing purposes)
- AWS CLI

## How-To

### Installing the worm

The worm can be installed automatically via Terraform

1. Automatic Installation
    a. Navigate to the `aws` directory in the project source code
2. Configure AWS CLI for your AWS account and run `terraform apply`, this will create all the necessary resources on the AWS account (AWS IAM roles, Lambda functions, EC2 instances, S3 buckets and Lambda triggers).
3. The newly discovered data for the AWS account can be downloaded through this link, https://bcit-8045-testing-bucket.s3.amazonaws.com/data  
4. Once the worm is installed it will be triggered automatically via AWS cloudwatch on a cron (every hour).This is an extremely disruptive behaviour, please only run this on a test AWS account to ensure no data is revealed unintentionally.

Notes:

- It is recommended to terminate all resources created by terraform to ensure no cost is incurred. This can be done via `terraform destroy`
- If you want to run the keylogger with more control and transparency for testing, the suggested method is by running the python file from the source code in github.
