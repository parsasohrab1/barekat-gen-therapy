terraform {
  required_version = ">= 1.6.0"

  required_providers {
    # aws = {
    #   source  = "hashicorp/aws"
    #   version = "~> 5.0"
    # }
  }
}

# Provider configuration — uncomment and configure for target cloud (AWS/GCP/Azure).
# provider "aws" {
#   region = var.aws_region
# }

# Phase 5: VPC, managed PostgreSQL, Redis, object storage, and Kubernetes cluster.
# See docs/ARCHITECTURE.md section 12 for deployment topology.
