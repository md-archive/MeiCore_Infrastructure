# Variables
CORE_COMPOSE := core/docker-compose.yaml
BUSINESS_COMPOSE := applications/business.redcat.best/docker-compose.yaml
MAIN_COMPOSE := applications/redcat.best/docker-compose.yaml

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

.PHONY: help deploy-core destroy-production deploy-business deploy-main deploy-all health-check

help: ## Show available targets
        @echo "$(GREEN)Available deployment targets:$(NC)"
        @awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

deploy-production: ## Deploy core infrastructure (Traefik, etc.)
        @echo "$(GREEN)🚀 Deploying core infrastructure...$(NC)"
        docker compose -f $(CORE_COMPOSE) --env-file environments/.prod.env up -d
        @echo "$(GREEN)✅ Core infrastructure deployed$(NC)"

destroy-production: ## Destroy core Infrastructure (traefik, etc.)
        @echo "${RED} Destroying current setup... ${NC}"
        docker compose -f ${CORE_COMPOSE} --env-file environments/.prod.env down -v
        @echo "${RED} DONE ${NC}"

deploy-business: ## Deploy business applications
        @echo "$(GREEN)🚀 Deploying business applications...$(NC)"
        docker compose -f $(BUSINESS_COMPOSE) up -d
        @echo "$(GREEN)✅ Business applications deployed$(NC)"

deploy-main: ## Deploy main site
        @echo "$(GREEN)🚀 Deploying main site...$(NC)"
        docker compose -f $(MAIN_COMPOSE) --env-file environments/.main.env up -d
        @echo "$(GREEN)✅ Main site deployed$(NC)"

destroy-main: ## Destroy main site
        @echo "$(YELLOW) Removing main site... $(NC)"
        docker compose -f $(MAIN_COMPOSE) --env-file environments/.main.env down -v
        @echo "$(YELLOW) Destruction complete $(NC)"

deploy-all: deploy-core ## Deploy everything in correct order
        @sleep 10  # Wait for core to be ready
        @$(MAKE) deploy-business
        @sleep 5   # Wait for business to be ready
        @$(MAKE) deploy-main
        @echo "$(GREEN)🎉 Full deployment completed$(NC)"

health-check: ## Check all services status
        @echo "$(GREEN)🔍 Checking core services...$(NC)"
        docker compose -f $(CORE_COMPOSE) ps
        @echo "$(GREEN)🔍 Checking business services...$(NC)"
        docker compose -f $(BUSINESS_COMPOSE) ps
        @echo "$(GREEN)🔍 Checking main site services...$(NC)"
        docker compose -f $(MAIN_COMPOSE) ps

stop-all: ## Stop all services
        @echo "$(YELLOW)🛑 Stopping all services...$(NC)"
        docker compose -f $(MAIN_COMPOSE)  --env-file environments/.main.env down
        #docker compose -f $(BUSINESS_COMPOSE) down
        docker compose -f $(CORE_COMPOSE)  --env-file environments/.prod.env down

restart-all: stop-all deploy-all ## Restart everything

logs-core: ## Show core service logs
        docker compose -f $(CORE_COMPOSE) logs -f

logs-business: ## Show business service logs
        docker compose -f $(BUSINESS_COMPOSE) logs -f

logs-main: ## Show main site logs
        docker compose -f $(MAIN_COMPOSE) logs -f