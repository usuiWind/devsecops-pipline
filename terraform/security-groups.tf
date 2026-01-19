resource "aws_security_group" "pod" {
  name_description = "Pod security group - minimal access"
  vpc_id           = module.vpc.vpc_id

  # Allow only necessary egress
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS only"
  }

  tags = {
    Name = "${var.project_name}-pod-sg"
  }
}