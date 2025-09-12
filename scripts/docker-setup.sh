#!/bin/bash

# Personal Blog Docker Setup Script
# This script sets up the development environment using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to setup environment files
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f .env.docker ]; then
            cp .env.docker .env
            print_success "Created .env from .env.docker template"
        else
            print_warning "No environment template found. Creating basic .env file..."
            cat > .env << EOF
# Basic environment configuration
DB_HOST=db
DB_NAME=blog_db
DB_USER=blog_user
DB_PASSWORD=blog_password
SECRET_KEY=change-this-secret-key-in-production
DEBUG=true
EOF
            print_success "Created basic .env file"
        fi
    else
        print_status ".env file already exists, skipping creation"
    fi
}

# Function to create init database script
create_init_db() {
    print_status "Creating database initialization script..."
    
    mkdir -p scripts
    cat > scripts/init-db.sql << 'EOF'
-- Initialize database for Personal Blog
-- This script runs automatically when PostgreSQL container starts

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database user if not exists (Docker will create the database)
-- Additional initialization can be added here as needed

-- Create indexes for performance (will be managed by Alembic)
-- This is just a placeholder for any initial setup

SELECT 'Database initialized successfully' as status;
EOF
    print_success "Created database initialization script"
}

# Function to build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build --parallel
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for PostgreSQL to be ready..."
    timeout 60 bash -c 'until docker-compose exec -T db pg_isready -U blog_user -d blog_db > /dev/null 2>&1; do sleep 2; done'
    
    if [ $? -eq 0 ]; then
        print_success "PostgreSQL is ready"
    else
        print_error "PostgreSQL failed to start within timeout"
        exit 1
    fi
    
    # Wait for backend
    print_status "Waiting for backend to be ready..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health > /dev/null 2>&1; do sleep 2; done'
    
    if [ $? -eq 0 ]; then
        print_success "Backend is ready"
    else
        print_warning "Backend health check failed, but continuing..."
    fi
    
    print_success "All services started successfully"
}

# Function to show service status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  Backend Docs: http://localhost:8000/docs"
    echo "  PostgreSQL: localhost:5432"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Run migrations inside backend container
    docker-compose exec backend alembic upgrade head
    
    if [ $? -eq 0 ]; then
        print_success "Database migrations completed"
    else
        print_warning "Database migrations failed or no migrations to run"
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_success "Services stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up containers and volumes..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
}

# Function to show help
show_help() {
    echo "Personal Blog Docker Setup Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       Build and start all services (default)"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show service status"
    echo "  logs        Show logs for all services"
    echo "  logs <svc>  Show logs for specific service (db, backend, frontend)"
    echo "  migrate     Run database migrations"
    echo "  cleanup     Stop services and remove volumes"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs backend"
    echo "  $0 migrate"
}

# Main script logic
main() {
    local command=${1:-start}
    
    case $command in
        start)
            check_docker
            check_docker_compose
            setup_env
            create_init_db
            start_services
            show_status
            ;;
        stop)
            check_docker
            check_docker_compose
            stop_services
            ;;
        restart)
            check_docker
            check_docker_compose
            stop_services
            start_services
            show_status
            ;;
        status)
            check_docker
            check_docker_compose
            show_status
            ;;
        logs)
            check_docker
            check_docker_compose
            show_logs $2
            ;;
        migrate)
            check_docker
            check_docker_compose
            run_migrations
            ;;
        cleanup)
            check_docker
            check_docker_compose
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"