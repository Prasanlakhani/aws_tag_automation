terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.5"
    }
  }
}

# S3 bucket
resource "aws_s3_bucket" "prasans3" {
  bucket = var.s3_name
}

# Lambda function
resource "aws_lambda_function" "tag_lambda" {
  filename      = "./code/main.zip"
  function_name = "tagging_lamda_tf_test"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.8"
  timeout       = 300
  source_code_hash = filebase64("./code/main.zip")

  depends_on = [aws_s3_bucket.prasans3]
}

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
          Service = "events.amazonaws.com",  # Corrected service name for EventBridge
        },
      },
    ],
  })
}

# IAM Policy for Lambda function
resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_policy_tf_test"
  description = "Policy for Lambda function"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["ec2:DescribeInstances", "ec2:CreateTags", "ec2:DeleteTags"],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action   = [
          "events:GetRule",  # Adjusted permissions for EventBridge
          "events:PutTargets",
          "events:PutRule",
        ],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket", "s3:DeleteObject"],
        Effect   = "Allow",
        Resource = [aws_s3_bucket.prasans3.arn, "${aws_s3_bucket.prasans3.arn}/*"],
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
  name        = "s3_event_rule_tf_test"
  description = "Event rule for S3 bucket events"

  event_pattern = jsonencode({
    source      = ["aws.s3"],
    detail      = {
      eventName = ["PutObject"],
    },
    resources   = [aws_s3_bucket.prasans3.arn],
  })
}

# Target for the EventBridge rule - Lambda function
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.s3_event_rule.name
  target_id = "lambda_target"
  arn       = aws_lambda_function.tag_lambda.arn

  depends_on = [aws_lambda_function.tag_lambda]
}
