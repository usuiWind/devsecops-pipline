# DevSecOps Pipeline

A security-focused DevSecOps reference pipeline that combines infrastructure-as-code, container hardening, runtime detection, and automated response.

## Architecture

- **Infrastructure**: AWS EKS cluster provisioned with Terraform
- **Application**: A hardened Flask API container
- **Security**: Kubernetes network policies, container scanning, and Falco runtime detection
- **Monitoring and audit**: CloudTrail, VPC Flow Logs, and Falco alerts

## Prerequisites

- AWS Account with appropriate permissions
- Terraform 1.0 or newer
- kubectl
- Docker
- Python 3.11 or newer
- AWS CLI configured

## Quick Start

### 1. Configure Environment Variables

Create or update a `.env` file in the project root (this file is not committed). Set at least:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_REGION` - AWS region (default: us-east-1)
- `SLACK_WEBHOOK_URL` - Slack webhook for Falco alerts (optional)
- Other configuration values as needed

For a complete checklist, see `SETUP.md`.

### 2. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

This will create:
- VPC with public/private subnets
- EKS cluster with managed node groups
- KMS encryption keys
- CloudTrail for audit logging
- S3 bucket for CloudTrail logs

### 3. Configure kubectl

After Terraform completes, configure kubectl:

```bash
aws eks update-kubeconfig --name devsecops-eks-cluster --region us-east-1
```

Verify connection:
```bash
kubectl get nodes
```

### 4. Build and Push Docker Image

```bash
# Build the image
docker build -t flask-api:latest -f docker/Dockerfile .

# Tag for your registry (replace with your registry)
docker tag flask-api:latest ghcr.io/your-org/flask-api:latest

# Push to registry
docker push ghcr.io/your-org/flask-api:latest
```

### 5. Deploy Application

Update the image in `kubernetes/deployment.yaml` if needed, then:

```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/network-policy.yaml
```

### 6. Verify Deployment

```bash
# Check pods
kubectl get pods

# Check services
kubectl get services

# View logs
kubectl logs -f deployment/flask-api
```

## Project Structure

```
.
├── app/                    # Flask application
│   ├── main.py            # Main application code
│   └── requirements.txt   # Python dependencies
├── terraform/              # Infrastructure as Code
│   ├── main.tf            # Main Terraform configuration
│   ├── variables.tf       # Variable definitions
│   ├── iam.tf             # IAM configuration
│   └── security-groups.tf # Security groups
├── docker/                # Docker configuration
│   └── Dockerfile         # Multi-stage Docker build
├── kubernetes/            # Kubernetes manifests
│   ├── deployment.yaml    # Application deployment
│   └── network-policy.yaml # Network security policies
├── falco/                 # Runtime security
│   ├── alert-handler.py   # Automated threat response
│   └── customs-rules.yaml # Custom Falco rules
├── attack-sim/            # Attack simulation scripts
└── .env                   # Environment variables (not in git)
```

## Security Features

### Infrastructure Security
- EKS cluster with encryption at rest
- Private subnets for worker nodes
- IMDSv2 enforcement
- CloudTrail audit logging
- KMS encryption for cluster secrets and related resources

### Container Security
- Non-root containers
- Read-only root filesystem
- Minimal Linux capabilities (drop all by default)
- Resource limits
- Security context enforcement

### Network Security
- Network policies (default deny)
- Restricted egress (HTTPS only)
- VPC isolation

### Runtime Security
- Falco for threat detection
- Automated pod isolation
- Automated pod termination for critical threats
- Slack alerting

## Testing

### Health Check

```bash
# Port forward to access the service
kubectl port-forward deployment/flask-api 5000:5000

# Test health endpoint
curl http://localhost:5000/health
```

### Attack Simulation

The `attack-sim/` directory contains scripts to test security controls:
- `crypto-miner` - Simulates crypto mining attack
- `network-connection` - Tests network policies
- `privilege-escalation.sh` - Tests privilege escalation detection
- `shell.sh` - Tests shell spawn detection

## Troubleshooting

### Terraform Issues

```bash
# If modules fail to download
terraform init -upgrade

# Check Terraform state
terraform show
```

### Kubernetes Issues

```bash
# Check cluster status
kubectl cluster-info

# Check node status
kubectl get nodes

# View pod events
kubectl describe pod <pod-name>
```

### Falco Issues

```bash
# Check Falco pods
kubectl get pods -n falco

# View Falco logs
kubectl logs -n falco -l app=falco
```

## Environment Variables

Key environment variables (see your local `.env` file for the full list):

- `AWS_REGION` - AWS region for resources
- `PROJECT_NAME` - Project name for resource naming
- `CLUSTER_NAME` - EKS cluster name
- `SLACK_WEBHOOK_URL` - Slack webhook for alerts
- `APP_VERSION` - Application version

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

**Warning**: This will delete all infrastructure including the EKS cluster and all data.

## Contributing

1. Follow security best practices
2. Run security scans before committing
3. Update documentation for any changes
4. Test in a development environment first

## License

[Your License Here]

