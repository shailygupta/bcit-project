data "aws_iam_policy_document" "main" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "main" {
  name               = "AWSLambdaExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.main.json
}

data "aws_iam_policy" "admin" {
  arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_role_policy_attachment" "admin" {
  policy_arn = data.aws_iam_policy.admin.arn
  role      = aws_iam_role.main.name
}

// Need to ensure the whole folder is zipped
data "archive_file" "main" {
  type        = "zip"
  source_dir = "../bin/attack"
  output_path = "main.zip"
}

// Lambda function
resource "aws_lambda_function" "main" {
  function_name    = "testing"
  filename         = "main.zip"
  source_code_hash = data.archive_file.main.output_base64sha256
  role             = aws_iam_role.main.arn
  runtime          = "python3.9"
  handler          = "main.lambda_handler"
  timeout          = 140
}

// trigger
resource "aws_cloudwatch_event_rule" "main" {
  name                = "run-lambda-function"
  description         = "Schedule lambda function"
  schedule_expression = "rate(60 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda-function-target" {
  target_id = "lambda-function-target"
  rule      = aws_cloudwatch_event_rule.main.name
  arn       = aws_lambda_function.main.arn
}

resource "aws_lambda_permission" "main" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.main.arn
}

// Test reosurces
// S3
resource "aws_s3_bucket" "main" {
  bucket = "bcit-project-test-bucket-shailygupta"

  tags = {
    Name        = "Comp 8045 Test Bucket"
    Environment = "Dev"
  }
}
//EC2
resource "aws_instance" "main" {
  ami           = "ami-0ceecbb0f30a902a6"
#   ami = "ami-060d3509162bcc386" // N. California AMI
  instance_type = "t2.micro"

  tags = {
    Name = "Testing-Instance"
  }
}
