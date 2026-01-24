#!/bin/bash
# Simulate privilege escalation (MITRE T1068)

echo "Simulating privilege escalation attempt..."
kubectl get pods -l app=flask-api -o name | head -1 | \
  xargs -I {} kubectl exec -it {} -- sudo -l

echo "Check Falco alerts for detection"