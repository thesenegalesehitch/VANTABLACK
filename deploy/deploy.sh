#!/bin/bash

# Vantablack Multi-Cloud Deployment Script
# Usage: ./deploy.sh [aws|gcp|azure|digitalocean|kubernetes] [environment]

set -e

CLOUD_PROVIDER="${1:-kubernetes}"
ENVIRONMENT="${2:-production}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_dependencies() {
    log "Checking dependencies..."
    
    local missing_deps=()
    
    # Check cloud-specific dependencies
    case "$CLOUD_PROVIDER" in
        aws)
            command -v aws >/dev/null 2>&1 || missing_deps+=("aws-cli")
            command -v terraform >/dev/null 2>&1 || missing_deps+=("terraform")
            ;;
        gcp)
            command -v gcloud >/dev/null 2>&1 || missing_deps+=("gcloud")
            command -v terraform >/dev/null 2>&1 || missing_deps+=("terraform")
            ;;
        azure)
            command -v az >/dev/null 2>&1 || missing_deps+=("azure-cli")
            command -v terraform >/dev/null 2>&1 || missing_deps+=("terraform")
            ;;
        kubernetes)
            command -v kubectl >/dev/null 2>&1 || missing_deps+=("kubectl")
            command -v helm >/dev/null 2>&1 || missing_deps+=("helm")
            ;;
    esac
    
    # Common dependencies
    command -v docker >/dev/null 2>&1 || missing_deps+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing_deps+=("docker-compose")
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing_deps[*]}"
    fi
    
    log "All dependencies found"
}

deploy_kubernetes() {
    log "Deploying to Kubernetes cluster..."
    
    # Build and push Docker images
    log "Building Docker images..."
    docker build -t vantablack-api:latest -f Dockerfile.api .
    docker build -t vantablack-worker:latest -f Dockerfile.worker .
    
    # Apply Kubernetes manifests
    log "Applying Kubernetes configurations..."
    kubectl apply -f deploy/kubernetes/namespace.yaml
    kubectl apply -f deploy/kubernetes/redis-deployment.yaml
    kubectl apply -f deploy/kubernetes/api-deployment.yaml
    kubectl apply -f deploy/kubernetes/ingress.yaml
    kubectl apply -f deploy/kubernetes/hpa.yaml
    
    # Wait for deployment to be ready
    log "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available deployment/vantablack-api --timeout=300s
    
    log "Kubernetes deployment completed successfully!"
    log "Access your deployment at: https://vantablack.your-domain.com"
}

deploy_aws() {
    log "Deploying to AWS..."
    
    # Build Docker image
    docker build -t vantablack-api:latest -f Dockerfile.api .
    
    # Push to ECR
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region)
    
    log "Logging into ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    log "Creating ECR repository..."
    aws ecr create-repository --repository-name vantablack --region $AWS_REGION || true
    
    log "Pushing image to ECR..."
    docker tag vantablack-api:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/vantablack:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/vantablack:latest
    
    log "AWS deployment completed!"
}

deploy_digitalocean() {
    log "Deploying to DigitalOcean..."
    
    # Build and tag image
    docker build -t vantablack-api:latest -f Dockerfile.api .
    
    # Login to DigitalOcean Container Registry
    doctl registry login
    
    # Tag and push image
    docker tag vantablack-api:latest registry.digitalocean.com/vantablack/vantablack:latest
    docker push registry.digitalocean.com/vantablack/vantablack:latest
    
    log "DigitalOcean deployment completed!"
}

# Health check function
health_check() {
    log "Performing health check..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/v5/health >/dev/null 2>&1; then
            log "Health check passed!"
            return 0
        fi
        
        warn "Health check attempt $attempt/$max_attempts failed"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    error "Health check failed after $max_attempts attempts"
}

# Main deployment function
deploy() {
    check_dependencies
    
    log "Starting deployment to $CLOUD_PROVIDER ($ENVIRONMENT environment)"
    
    case "$CLOUD_PROVIDER" in
        kubernetes)
            deploy_kubernetes
            ;;
        aws)
            deploy_aws
            ;;
        digitalocean)
            deploy_digitalocean
            ;;
        *)
            error "Unsupported cloud provider: $CLOUD_PROVIDER"
            ;;
    esac
    
    log "Deployment completed successfully!"
    log "Next steps:"
    log "1. Configure your DNS to point to the load balancer"
    log "2. Set up SSL certificates"
    log "3. Configure environment variables for production"
}

# Run deployment
deploy "$@"

# Perform final health check
health_check