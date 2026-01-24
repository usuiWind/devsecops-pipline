variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "devsecops-pipeline"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "devsecops-eks-cluster"
}
