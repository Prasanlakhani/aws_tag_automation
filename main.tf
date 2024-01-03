provider "aws" {
  region = var.region_name  # Change this to your desired AWS region
}

# Define the S3 bucket for Terraform state
resource "aws_s3_bucket" "terraform_state_bucket" {
  bucket = var.s3_tfstate_name  # Replace with your desired bucket name
  acl    = "private"
}

# Configure the backend to use S3
terraform {
  backend "s3" {
    bucket         = aws_s3_bucket.terraform_state_bucket.bucket
    key            = "terraform.tfstate"
    region         = var.region_name  
    #encrypt        = true
    #dynamodb_table = "terraform_lock"  # Optional: Use DynamoDB for state locking
  }
}
# S3 bucket
resource "aws_s3_bucket" "prasans3" {
  bucket = var.s3_name
  acl    = "private"
}

# Lambda function
resource "aws_lambda_function" "example_lambda" {
  filename      = "./code/main.py"  # Update with the actual path to your Lambda function code
  function_name = "tagging_lamda"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.8"  # Update with the runtime your Lambda function uses
  
  timeout = 300  # Timeout set to 5 minutes (300 seconds)

  source_code_hash = filebase64("./code/main.py")

  depends_on = [aws_s3_bucket.prasans3]
}

#
#data "archive_file" "archive_code" {
#  type        = "zip"
#  source_dir  = pathexpand("code/")
#  output_path = pathexpand("code.zip")
#}

# IAM Role for Lambda function
resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com",
        },
      },
	  {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "scheduler.amazonaws.com",
        },
      },
    ],
  })
}

# IAM Policy for Lambda function
resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_policy"
  description = "Policy for Lambda function"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ec2:DescribeInstances","ec2:CreateTags","ec2:DeleteTags"],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action   = ["scheduler:GetSchedule","scheduler:UpdateSchedule","scheduler:CreateSchedule","scheduler:ListSchedules","scheduler:DeleteSchedule"],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action   = ["s3:GetObject","s3:PutObject","s3:ListBucket","s3:DeleteObject"],
        Effect   = "Allow",
        Resource = aws_s3_bucket.prasans3.arn,
      },
    ],
  })
}



# Attach Lambda execution role policy
resource "aws_iam_role_policy_attachment" "lambda_exec_attachment" {
  policy_arn = aws_iam_policy.lambda_policy.arn
  role       = aws_iam_role.lambda_exec.name
}

# EventBridge rule to trigger Lambda function on S3 object creation
resource "aws_cloudwatch_event_rule" "s3_event_rule" {
  name        = "s3_event_rule"
  description = "Event rule for S3 bucket events"

  event_pattern = jsonencode({
    source      = ["aws.s3"],
    detail      = {
      eventName = ["PutObject"],  # You can customize this based on the S3 events you want to trigger the Lambda function
    },
    resources   = [aws_s3_bucket.prasans3.arn],
  })
}

## Target for the EventBridge rule - Lambda function
#resource "aws_cloudwatch_event_target" "lambda_target" {
#  rule      = aws_cloudwatch_event_rule.s3_event_rule.name
#  target_id = "lambda_target"
#  arn       = aws_lambda_function.example_lambda.arn
#}



##########################################

# IAM Policy for Lambda function
resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_policy"
  description = "Policy for Lambda function"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "logs:CreateLogGroup",
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = aws_iam_role.lambda_exec.arn,
      },
      {
        Action   = "events:PutRule",
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action   = "events:PutTargets",
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action   = "s3:GetObject",
        Effect   = "Allow",
        Resource = aws_s3_bucket.prasans3.arn,
      },
    ],
  })
}





{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::prasans3/*",  // Replace "prasans3" with your S3 bucket name
        "arn:aws:s3:::prasans3"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
		"scheduler:GetSchedule",
		"scheduler:UpdateSchedule",
		"scheduler:CreateSchedule",
		"scheduler:ListSchedules",
		"scheduler:DeleteSchedule"
		
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:CreateTags",
        "ec2:DeleteTags"
      ],
      "Resource": "*"
    }
  ]
}



##############################################
