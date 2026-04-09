provider "aws" {
  region = "us-east-1"
}

# ❌ Public S3 bucket
resource "aws_s3_bucket" "bad_bucket" {
  bucket = "my-open-bucket"

  acl = "public-read-write"   # ❌ public access

  versioning {
    enabled = false   # ❌ versioning disabled
  }
}

# ❌ Open Security Group
resource "aws_security_group" "bad_sg" {
  name = "open-sg"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # ❌ open to world
  }
}

# ❌ EC2 with hardcoded secret
resource "aws_instance" "bad_ec2" {
  ami           = "ami-123456"
  instance_type = "t2.micro"

  user_data = <<EOF
    #!/bin/bash
    echo "password=admin123" >> /etc/config   # ❌ hardcoded password
  EOF
}
