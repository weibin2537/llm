Chatbox - Modern AI Chatbot Application
A Kubernetes-based deployment of a chatbot application using DeepSeek LLM, with comprehensive monitoring, CI/CD pipeline, and modern infrastructure.

Architecture
The application consists of three main components:

Frontend: React-based UI that provides chat interface
Backend: Python FastAPI service that processes requests
Model Service: DeepSeek LLM running via Ollama
The application is deployed on Kubernetes with:

Istio for service mesh and traffic routing
Prometheus and Grafana for monitoring
Jenkins for CI/CD
Helm for package management
Prerequisites
Docker Desktop with Kubernetes enabled
Helm
Istio
Lens (for Kubernetes management)
kubectl
make (optional, for using the Makefile)
Local Development Setup
Clone the repository
bash
git clone https://github.com/yourusername/chatbox.git
cd chatbox
Set up local environment
bash
make setup-local
This will:

Install Istio
Set up Prometheus and Grafana
Configure a local Docker registry
Build and deploy the application
bash
make all
This will:

Build Docker images
Push to local registry
Deploy to Kubernetes with Helm
Access the application
Add the following to your /etc/hosts file:

127.0.0.1 myapp.local
Then access the application at: http://myapp.local

Monitoring
Prometheus
Access Prometheus via port-forwarding:

bash
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
Then visit: http://localhost:9090

Grafana
Access Grafana via port-forwarding:

bash
kubectl port-forward -n monitoring svc/grafana 3000:80
Then visit: http://localhost:3000

Login with:

Username: admin
Password: (Get it with kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode)
CI/CD Pipeline
The Jenkins pipeline (Jenkinsfile) automates:

Building Docker images
Pushing to registry
Deploying to Kubernetes
Verifying deployment success
Setting up Jenkins:
Deploy Jenkins using the provided docker-compose.yml in the cicd directory:
bash
cd cicd
docker-compose up -d
Access Jenkins at http://localhost:8080
Configure Jenkins:
Install the Kubernetes and Docker plugins
Configure Docker credentials
Configure Kubernetes connection
Create a pipeline job pointing to your repository
Component Details
Frontend
React-based UI
Communicates with backend via HTTP
Containerized with Node.js
Backend
Python FastAPI service
Handles request processing and LLM interaction
Provides metrics and health checks
Communicates with the model service
Model Service
DeepSeek LLM running via Ollama
Exposes API for inference
Includes metrics collection
Helm Chart Structure
The application is packaged as a Helm chart with the following structure:

chatbox/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── frontend/
│   ├── backend/
│   ├── model/
│   ├── istio/
│   └── monitoring/
Customize the deployment by modifying the values.yaml file.

Cleaning Up
To remove all deployed resources:

bash
make clean
Troubleshooting
Common Issues
Images not pulling
Ensure your local registry is running: docker ps | grep registry
Check image paths in values.yaml
Istio sidecar not injecting
Verify namespace is labeled: kubectl get namespace -L istio-injection
Restart pods if needed
Model not loading
Check model pod logs: kubectl logs -f <model-pod-name>
Ensure PVC is provisioned correctly
License
MIT License

