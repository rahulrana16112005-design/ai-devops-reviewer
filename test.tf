provider "aws" {
  region = "us-east-1"
}

# ✅ Good S3 bucket (secure)
resource "aws_s3_bucket" "good_bucket" {
  bucket = "my-secure-bucket"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# ❌ Bad S3 bucket (insecure)
resource "aws_s3_bucket" "bad_bucket" {
  bucket = "my-open-bucket"

  acl = "public-read-write"   # ❌ public access

  versioning {
    enabled = false     # ❌ no versioning
  }
}

# ❌ Bad Security Group
resource "aws_security_group" "bad_sg" {
  name = "open-sg"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # ❌ open to world
  }
}

# ✅ Good Security Group
resource "aws_security_group" "good_sg" {
  name = "restricted-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["192.168.1.0/24"]  # ✅ restricted access
  }
}

# ❌ Bad EC2 instance
resource "aws_instance" "bad_ec2" {
  ami           = "ami-123456"
  instance_type = "t2.micro"

  user_data = <<EOF
    #!/bin/bash
    echo "password=admin123" >> /etc/config   # ❌ hardcoded secret
  EOF
}

# ✅ Better EC2 instance
resource "aws_instance" "good_ec2" {
  ami           = "ami-123456"
  instance_type = "t3.micro"

  metadata_options {
    http_tokens = "required"   # ✅ IMDSv2 enforced
  }

  tags = {
    Name = "secure-instance"
  }
}
