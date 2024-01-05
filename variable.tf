variable "region_name" {
  type = string
  default     = "ap-south-1"
  description = "Aws Region"
}

variable "s3_name" {
  type = string
  default     = "tagautomations3bucketpoc"
  description = "S3 bucket name, where the .json file will be stored"
}

variable "lambda_name" {
  type = string
  default     = "tag_automation_lambda_poc"
  description = "name of the lamda function"
}

variable "role_name" {
  type = string
  default     = "tag_automation_role_poc"
  description = "aws role name"
}

variable "policy_name" {
  type = string
  default     = "tag_automation_policy_poc"
  description = "aws policy name"
}



