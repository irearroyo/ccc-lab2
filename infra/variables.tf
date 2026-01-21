variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC (must not overlap with partner's VPC)"
  type        = string
  default     = "10.0.0.0/24"
}

variable "availability_zone" {
  description = "Availability zone for subnet"
  type        = string
  default     = "us-east-1a"
}

variable "s3_bucket_suffix" {
  description = "Suffix for S3 bucket name (e.g., your-initials-random)"
  type        = string
}

variable "api_gateway_invoke_url" {
  description = "API Gateway invoke URL (will be output after creation)"
  type        = string
  default     = ""
}
