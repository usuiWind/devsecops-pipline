# Setup Checklist

Use this checklist to set up and test the DevSecOps pipeline end to end.

## Pre-Deployment Checklist

### 1. AWS Account Setup
- [ ] Create AWS account or use existing
- [ ] Create IAM user with programmatic access
- [ ] Attach policies: `AmazonEKSClusterPolicy`, `AmazonEKSWorkerNodePolicy`, `AmazonEC2FullAccess`, `AmazonVPCFullAccess`, `AmazonS3FullAccess`
- [ ] Save Access Key ID and Secret Access Key

### 2. Environment Configuration
- [ ] Create or update the `.env` file (local only)
- [ ] Set `AWS_ACCESS_KEY_ID` in `.env`
- [ ] Set `AWS_SECRET_ACCESS_KEY` in `.env`
- [ ] Set `AWS_REGION` (default: us-east-1)
- [ ] Set `PROJECT_NAME` (default: devsecops-pipeline)
- [ ] Set `CLUSTER_NAME` (default: devsecops-eks-cluster)
- [ ] Optional: Set `SLACK_WEBHOOK_URL` for Falco alerts

### 3. Local Tools Installation
- [ ] Install Terraform >= 1.0
- [ ] Install AWS CLI
- [ ] Install kubectl
- [ ] Install Docker
- [ ] Configure AWS CLI: `aws configure`

## Deployment Steps

### Step 1: Deploy Infrastructure
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Expected Output:**
- VPC created
- EKS cluster created
- KMS key created
- CloudTrail configured
- S3 bucket for logs created

**Time:** ~15-20 minutes

### Step 2: Configure kubectl
```bash
aws eks update-kubeconfig --name devsecops-eks-cluster --region us-east-1
kubectl get nodes
```

**Verify:** You should see 2 nodes in Ready state

### Step 3: Build Docker Image
```bash
# From project root
docker build -t flask-api:latest -f docker/Dockerfile .

# Tag for your registry (update registry URL)
docker tag flask-api:latest ghcr.io/your-org/flask-api:latest

# Login to registry (if using private registry)
# docker login ghcr.io

# Push image
docker push ghcr.io/your-org/flask-api:latest
```

**Note:** Update `kubernetes/deployment.yaml` line 30 with your image URL

### Step 4: Deploy Application
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/network-policy.yaml
```

**Verify:**
```bash
kubectl get pods
kubectl get deployments
```

### Step 5: Test Application
```bash
# Port forward
kubectl port-forward deployment/flask-api 5000:5000

# In another terminal
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "flask-api",
  "version": "1.0.0"
}
```

## Post-Deployment Verification

### Infrastructure
- [ ] EKS cluster is running
- [ ] Nodes are in Ready state
- [ ] CloudTrail is logging
- [ ] S3 bucket has CloudTrail logs

### Application
- [ ] Pods are running (3 replicas)
- [ ] Health endpoint responds
- [ ] Network policies are applied
- [ ] Security context is enforced

### Security
- [ ] Containers run as non-root
- [ ] Network policies restrict traffic
- [ ] Resource limits are set
- [ ] Read-only filesystem enforced

## Testing Security Features

### Test Network Policies
```bash
# Try to access from unauthorized pod (should fail)
kubectl run test-pod --image=busybox --rm -it -- wget -O- http://flask-api:5000/health
```

### Test Falco (if installed)
```bash
# Run attack simulation
cd attack-sim
./privilege-escalation.sh
```

## Troubleshooting

### Terraform Errors
- **Error: "Invalid region"** → Check `AWS_REGION` in `.env`
- **Error: "Access denied"** → Check IAM permissions
- **Error: "Bucket already exists"** → CloudTrail bucket name must be globally unique

### Kubernetes Errors
- **Pods not starting** → Check node resources: `kubectl describe nodes`
- **Image pull errors** → Verify image URL in deployment.yaml
- **Network policy blocking** → Check network-policy.yaml

### Application Errors
- **Health check failing** → Check pod logs: `kubectl logs deployment/flask-api`
- **Port forwarding issues** → Verify pod is running: `kubectl get pods`

## Cleanup

To destroy all resources:
```bash
cd terraform
terraform destroy
```

**Warning:** This deletes everything including the EKS cluster!

## Next Steps

1. Set up Falco for runtime security
2. Configure CI/CD pipeline
3. Set up monitoring and alerting
4. Configure backup strategies
5. Review and customize security policies

