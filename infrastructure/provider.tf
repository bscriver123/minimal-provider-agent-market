terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"
  backend "s3" {
    bucket         = "minimal-provider-agent-market-test-terraform-state"
    key            = "terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "minimal-provider-agent-market-test-terraform-lock-table"
  }
}

provider "aws" {
  region = var.aws_region
} 