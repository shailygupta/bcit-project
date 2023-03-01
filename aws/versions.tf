// Author: Shaily Gupta
// Purpose: BCIT COMP8045
// Student ID: A00952989

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}
