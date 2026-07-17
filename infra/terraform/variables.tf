variable "project_name" {
  description = "Project identifier"
  type        = string
  default     = "barekat-gen-therapy"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for cloud resources"
  type        = string
  default     = "eu-central-1"
}
