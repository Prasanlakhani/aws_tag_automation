variable "region_name" {
  type = string
  default     = "ap-south-1"
  #description = "The ID of the project where this VPC will be created"
}

variable "s3_tfstate_name" {
  type = string
  default     = "tagautomations3bucket-terraform-state-bucket"
  description = "The ID of the project where this VPC will be created"
}

variable "s3_name" {
  type = string
  default     = "tagautomations3bucket"
  description = "The ID of the project where this VPC will be created"
}
