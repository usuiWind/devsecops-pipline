#!/bin/bash
# Simulate container shell spawn (MITRE T1059)

echo "Simulating shell spawn in container..."
kubectl get pods -l app=flask-api -o name | head -1 | \
  xargs -I {} kubectl exec -it {} -- /bin/sh -c "echo 'Shell spawned'"

echo "Check Falco alerts for detection"