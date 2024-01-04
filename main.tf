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
  #acl    = "private"
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "./code/main.py"
  output_path = "main.zip"
}

# Lambda function
resource "aws_lambda_function" "tag_lambda" {
  filename      = "main.zip"
  function_name = "tagging_lamda_tf_test"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.8"
  timeout       = 300
  source_code_hash = data.archive_file.lambda.output_base64sha256
  
    environment {
    variables = {
      s3storage = var.s3_name
    }
	}
  
#  # S3 bucket trigger configuration
#  event_source {
#    s3 {
#      bucket         = aws_s3_bucket.prasans3.id
#      events         = ["s3:ObjectCreated:Put"]
#      filter_suffix  = ".json"  # Only trigger on objects with this suffix
#    }
#  }

  depends_on = [aws_s3_bucket.prasans3]
}

resource "aws_s3_bucket_notification" "aws-lambda-trigger" {
  bucket = aws_s3_bucket.prasans3.id
  
  lambda_function {
    lambda_function_arn = aws_lambda_function.tag_lambda.arn
    events              = ["s3:ObjectCreated:Put"]
	filter_suffix = ".json"
	
  #depends_on = [aws_s3_bucket.prasans3, aws_lambda_function.tag_lambda]
  }
}

resource "aws_lambda_permission" "test" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tag_lambda.arn
  principal = "s3.amazonaws.com"
  source_arn = aws_s3_bucket.prasans3.arn
  
  depends_on = [aws_lambda_function.tag_lambda, aws_s3_bucket_notification.aws-lambda-trigger]
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
          Service = "scheduler.amazonaws.com",
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
          "scheduler:GetSchedule",
          "scheduler:UpdateSchedule",
          "scheduler:CreateSchedule",
          "scheduler:ListSchedules",
          "scheduler:DeleteSchedule",
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

## EventBridge rule to trigger Lambda function on S3 object creation
#resource "aws_cloudwatch_event_rule" "s3_event_rule" {
#  name        = "s3_event_rule_tf_test"
#  description = "Event rule for S3 bucket events"
#
#  event_pattern = jsonencode({
#    source      = ["aws.s3"],
#    detail      = {
#      eventName = ["PutObject"],  # You can customize this based on the S3 events you want to trigger the Lambda function
#    },
#    resources   = [aws_s3_bucket.prasans3.arn],
#  })
#}

## Target for the EventBridge rule - Lambda function
#resource "aws_cloudwatch_event_target" "lambda_target" {
#  rule      = aws_cloudwatchevent_rule.s3_event_rule.name
#  target_id = "lambda_target"
#  arn       = aws_lambda_function.tag_lambda.arn
#  
#    depends_on = [aws_lambda_function.tag_lambda]
#}
