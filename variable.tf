variable "region_name" {
  type = string
  default     = "us-east-1"
  description = "Aws Region"
}

variable "s3_name" {
  type = string
  default     = "tagautomations3buckettest"
  description = "S3 bucket name, where the .json file will be stored"
}

variable "lambda_name" {
  type = string
  default     = "tag_automation_lambda_test"
  description = "name of the lamda function"
}

variable "role_name" {
  type = string
  default     = "tag_automation_role_test"
  description = "aws role name"
}

variable "policy_name" {
  type = string
  default     = "tag_automation_policy_test"
  description = "aws policy name"
}



