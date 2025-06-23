variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "ai-agent-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.24"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}