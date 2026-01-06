variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "product-inventory"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}
