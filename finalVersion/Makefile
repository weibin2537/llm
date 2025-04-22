.PHONY: build push deploy setup-local clean

# Variables
DOCKER_REGISTRY ?= localhost:5000
PROJECT_NAME ?= chatbox
TAG ?= latest
KUBECONFIG ?= ~/.kube/config
NAMESPACE ?= chatbox
HELM_RELEASE_NAME ?= chatbox
HELM_CHART_DIR ?= ./chatbox

# Build all Docker images
build:
	docker build -t $(DOCKER_REGISTRY)/$(PROJECT_NAME)-frontend:$(TAG) -f frontend/Dockerfile frontend/
	docker build -t $(DOCKER_REGISTRY)/$(PROJECT_NAME)-backend:$(TAG) -f backend/Dockerfile backend/
	docker build -t $(DOCKER_REGISTRY)/$(PROJECT_NAME)-model:$(TAG) -f deepseek/Dockerfile deepseek/

# Push all Docker images
push:
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)-frontend:$(TAG)
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)-backend:$(TAG)
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)-model:$(TAG)

# Deploy to local Kubernetes with Helm
deploy:
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl label namespace $(NAMESPACE) istio-injection=enabled --overwrite
	helm upgrade --install $(HELM_RELEASE_NAME) $(HELM_CHART_DIR) \
		--namespace=$(NAMESPACE) \
		--set frontend.image.tag=$(TAG) \
		--set backend.image.tag=$(TAG) \
		--set model.image.tag=$(TAG) \
		--set global.domain=myapp.local

# Setup local Kubernetes with necessary components
setup-local:
	# Install Istio
	curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.19.0 sh -
	cd istio-1.19.0 && ./bin/istioctl install --set profile=demo -y

	# Install Prometheus and Grafana using Helm
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo add grafana https://grafana.github.io/helm-charts
	helm repo update

	# Install Prometheus
	helm install prometheus prometheus-community/prometheus \
		--namespace monitoring \
		--create-namespace \
		--set server.persistentVolume.enabled=true \
		--set server.persistentVolume.size=10Gi

	# Install Grafana
	helm install grafana grafana/grafana \
		--namespace monitoring \
		--set persistence.enabled=true \
		--set persistence.size=5Gi \
		--set service.type=ClusterIP

	# Get Grafana admin password
	@echo "Grafana admin password: "
	@kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

	# Install local registry if it doesn't exist
	@if [ -z "$(shell docker ps -q -f name=registry)" ]; then \
		docker run -d -p 5000:5000 --restart=always --name registry registry:2; \
	fi

# Clean up resources
clean:
	helm uninstall $(HELM_RELEASE_NAME) --namespace=$(NAMESPACE) || true
	kubectl delete namespace $(NAMESPACE) || true

all: build push deploy

help:
	@echo "Available targets:"
	@echo "  build         - Build all Docker images"
	@echo "  push          - Push all Docker images to local registry"
	@echo "  deploy        - Deploy application to Kubernetes with Helm"
	@echo "  setup-local   - Setup local environment with Istio, Prometheus, and Grafana"
	@echo "  clean         - Remove deployed resources"
	@echo "  all           - Build, push, and deploy"
	@echo ""
	@echo "Variables:"
	@echo "  DOCKER_REGISTRY - Docker registry address (default: localhost:5000)"
	@echo "  TAG            - Docker image tag (default: latest)"
	@echo "  NAMESPACE      - Kubernetes namespace (default: chatbox)"
