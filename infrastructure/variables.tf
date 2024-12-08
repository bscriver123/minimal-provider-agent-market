variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "foundation_model_name" {
  description = "Name of the foundation model"
  type        = string
}

variable "environment" {
  description = "Environment (dev, prod, etc.)"
  type        = string
  default     = "dev"
}


variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "market_api_key" {
  description = "Agent Market API key"
  type        = string
  sensitive   = true
}

variable "github_pat" {
  description = "GitHub Personal Access Token"
  type        = string
  sensitive   = true
}

variable "max_bid" {
  description = "Maximum bid amount for proposals"
  type        = string
  default     = "0.01"
}

variable "git_branch" {
  description = "Git branch to checkout"
  type        = string
  default     = "main"
} 