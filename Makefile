.PHONY: build_iotsimulator install_kind create_kind_cluster install_kubectl \
	create_docker_registry connect_registry_to_kind_network connect_registry_registry \
	create_kind_cluster_with_registry delete_kind_cluster delete_docker_registry \
	push_docker_image_to_local_registry build deploy_all_resources

build_iotsimulator:
	docker build -t localhost:5555/temperature-service:latest .

push_docker_image_to_local_registry: create_docker_registry build_iotsimulator
	docker push localhost:5555/temperature-service:latest

install_kind:
	chmod +x ./kind && \
		./kind --version

create_kind_cluster: install_kind install_kubectl
	./kind create cluster --name iotsimulator --config ./k8s/kind-config.yaml || true && \
		kubectl get nodes && \
		kubectl config use-context kind-iotsimulator

install_kubectl:
	if ! command -v kubectl >/dev/null 2>&1; then \
		echo "kubectl not found. Installing via Homebrew..."; \
		brew install kubectl; \
	else \
		echo "kubectl is already installed."; \
	fi

create_docker_registry:
	if ! docker ps | grep -q 'local-registry'; \
	then docker run -d -p 5555:5000 --name local-registry --restart=always registry:2; \
	else echo "---> local-registry is already running. There's nothing to do here."; \
	fi

connect_registry_to_kind_network:
	docker network connect kind local-registry || true

connect_registry_registry: connect_registry_to_kind_network
	kubectl apply -f ./k8s/kind-configmap.yaml

create_kind_cluster_with_registry:
	$(MAKE) create_kind_cluster && $(MAKE) connect_registry_registry
	
delete_kind_cluster: delete_docker_registry
	./kind delete cluster --name iotsimulator

delete_docker_registry:
	docker stop local-registry && docker rm local-registry

build:
	$(MAKE) push_docker_image_to_local_registry && $(MAKE) create_kind_cluster_with_registry  && $(MAKE) deploy_all_resources

deploy_all_resources:
	kubectl apply -k github.com/mfenerich/postgres-operator/manifests && \
		kubectl rollout status deployment/postgres-operator --timeout=120s && \
		kubectl apply -f ./k8s/postgres-secret.yaml && \
		kubectl apply -f ./k8s/timescaledb-cluster.yaml && \
		kubectl apply -f ./k8s/iotsimulator-config.yaml && \
		kubectl apply -f ./k8s/iotsimulator-secret.yaml && \
		kubectl apply -f ./k8s/app-deployment.yaml && \
		kubectl apply -f ./k8s/iotsimulator-service.yaml
