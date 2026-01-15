# Terraform configuration for AWS deployment
# This creates EC2 instance with all necessary resources

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed for SSH"
  type        = string
  default     = "0.0.0.0/0"  # Change to your IP for security
}

# VPC and Networking
data "aws_vpc" "default" {
  default = true
}

# Security Group
resource "aws_security_group" "ai_devops_sg" {
  name        = "ai-devops-platform-sg"
  description = "Security group for AI DevOps Platform"
  vpc_id      = data.aws_vpc.default.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
    description = "SSH access"
  }

  # Jenkins
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Jenkins web UI"
  }

  # Streamlit
  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Streamlit dashboard"
  }

  # Flask
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Flask application"
  }

  # HTTP (for nginx if used)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  # HTTPS (for nginx with SSL)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "ai-devops-platform-sg"
  }
}

# Get latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# User data script to setup EC2
data "template_file" "user_data" {
  template = file("${path.module}/user-data.sh")
}

# EC2 Instance
resource "aws_instance" "ai_devops_server" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.ai_devops_sg.id]

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
  }

  user_data = data.template_file.user_data.rendered

  tags = {
    Name = "ai-devops-platform"
  }
}

# Elastic IP
resource "aws_eip" "ai_devops_eip" {
  instance = aws_instance.ai_devops_server.id
  domain   = "vpc"

  tags = {
    Name = "ai-devops-platform-eip"
  }
}

# Outputs
output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.ai_devops_server.id
}

output "public_ip" {
  description = "Public IP address"
  value       = aws_eip.ai_devops_eip.public_ip
}

output "jenkins_url" {
  description = "Jenkins URL"
  value       = "http://${aws_eip.ai_devops_eip.public_ip}:8080"
}

output "streamlit_url" {
  description = "Streamlit URL"
  value       = "http://${aws_eip.ai_devops_eip.public_ip}:8501"
}

output "flask_url" {
  description = "Flask URL"
  value       = "http://${aws_eip.ai_devops_eip.public_ip}:5000"
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i ${var.key_name}.pem ec2-user@${aws_eip.ai_devops_eip.public_ip}"
}
