#!/bin/bash

# Set namespace
NAMESPACE="chatbox"

echo "===== Checking pod status ====="
kubectl get pods -n $NAMESPACE

echo "===== Checking service status ====="
kubectl get svc -n $NAMESPACE

echo "===== Checking endpoints ====="
kubectl get endpoints -n $NAMESPACE

echo "===== Creating debug pod ====="
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: network-debug
  namespace: $NAMESPACE
spec:
  containers:
  - name: network-debug
    image: nicolaka/netshoot
    command: ["sleep", "3600"]
EOF

echo "Waiting for debug pod to be ready..."
kubectl wait --for=condition=Ready pod/network-debug -n $NAMESPACE --timeout=60s

echo "===== Testing connectivity from debug pod ====="
echo "Testing DNS resolution for backend service:"
kubectl exec -n $NAMESPACE network-debug -- nslookup chatbox-backend

echo "Testing connectivity to backend service:"
kubectl exec -n $NAMESPACE network-debug -- curl -v http://chatbox-backend:8000/health

echo "Testing connectivity to model service:"
kubectl exec -n $NAMESPACE network-debug -- curl -v http://chatbox-model:11434/api/health

echo "===== Checking logs from frontend pod ====="
FRONTEND_POD=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=chatbox-frontend -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n $NAMESPACE $FRONTEND_POD

echo "===== Checking logs from backend pod ====="
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=chatbox-backend -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n $NAMESPACE $BACKEND_POD

echo "===== Debug completed ====="
echo "To clean up the debug pod, run: kubectl delete pod network-debug -n $NAMESPACE"
