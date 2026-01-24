#!/usr/bin/env python3
"""
Falco Alert Handler - Automated Response
Receives Falco alerts and takes action
"""

import json
import sys
import os
import requests
from kubernetes import client, config

# Load K8s config
config.load_incluster_config()
v1 = client.CoreV1Api()

# Load configuration from environment variables
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/YOUR/WEBHOOK")
FALCO_NAMESPACE = os.getenv("FALCO_ALERT_NAMESPACE", "default")
ENABLE_AUTO_RESPONSE = os.getenv("FALCO_ENABLE_AUTO_RESPONSE", "true").lower() == "true"

def send_slack_alert(alert):
    """Send alert to Slack"""
    message = {
        "text": f"🚨 Falco Alert: {alert['rule']}",
        "attachments": [{
            "color": "danger",
            "fields": [
                {"title": "Priority", "value": alert['priority'], "short": True},
                {"title": "Container", "value": alert['output_fields'].get('container.name'), "short": True},
                {"title": "Details", "value": alert['output']}
            ]
        }]
    }
    requests.post(SLACK_WEBHOOK, json=message)

def isolate_pod(pod_name, namespace=None):
    """Apply network policy to isolate pod"""
    if namespace is None:
        namespace = FALCO_NAMESPACE
    
    isolation_policy = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {"name": f"isolate-{pod_name}"},
        "spec": {
            "podSelector": {"matchLabels": {"name": pod_name}},
            "policyTypes": ["Ingress", "Egress"]
        }
    }
    
    networking_v1 = client.NetworkingV1Api()
    networking_v1.create_namespaced_network_policy(namespace, isolation_policy)

def terminate_pod(pod_name, namespace=None):
    """Terminate suspicious pod"""
    if namespace is None:
        namespace = FALCO_NAMESPACE
    v1.delete_namespaced_pod(pod_name, namespace)

def main():
    """Process Falco alert"""
    alert = json.load(sys.stdin)
    
    priority = alert.get('priority')
    rule = alert.get('rule')
    container_name = alert['output_fields'].get('container.name')
    
    print(f"Alert received: {rule} - {priority}")
    
    # Send to Slack
    if SLACK_WEBHOOK and SLACK_WEBHOOK != "https://hooks.slack.com/services/YOUR/WEBHOOK":
        try:
            send_slack_alert(alert)
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    else:
        print("Warning: SLACK_WEBHOOK_URL not configured, skipping Slack notification")
    
    # Automated response based on severity (only if enabled)
    if ENABLE_AUTO_RESPONSE and priority == "CRITICAL":
        print(f"CRITICAL alert - Isolating pod {container_name}")
        try:
            isolate_pod(container_name)
        except Exception as e:
            print(f"Failed to isolate pod: {e}")
        
        if "Crypto Mining" in rule:
            print(f"Terminating pod {container_name}")
            try:
                terminate_pod(container_name)
            except Exception as e:
                print(f"Failed to terminate pod: {e}")

if __name__ == "__main__":
    main()