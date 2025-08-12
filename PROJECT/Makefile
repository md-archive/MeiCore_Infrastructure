# Variables
CORE_COMPOSE := core/docker-compose.yaml
BUSINESS_COMPOSE := applications/business.redcat.best/docker-compose.yaml
MAIN_COMPOSE := applications/redcat.best/docker-compose.yaml
STORE_COMPOSE := applications/redcat.best.shop/docker-compose.yaml

PROD_ENV := environments/.prod.env
DEV_ENV := environments/.main.env
STAGE_ENV := environments/.shop.env
# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

.PHONY: help start-all stop-all run-core stop-core run-main stop-main health-check

help: ## Show available targets
	@echo "$(GREEN)Available deployment targets:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

start-all: ## Deploy core services
	@echo "$(GREEN) Deploying services...$(NC)"
	docker compose -f $(CORE_COMPOSE) --env-file $(PROD_ENV) up -d
	docker compose -f $(MAIN_COMPOSE) --env-file $(PROD_ENV) up -d
	docker compose -f $(STORE_COMPOSE) --env-file $(PROD_ENV) up -d
	@echo "$(GREEN) All Services have been successfully deployed $(NC)"

stop-all: ## Stop all services
	@echo "$(YELLOW)🛑 Stopping all services... 🛑$(NC)"
	docker compose -f $(CORE_COMPOSE) --env-file $(PROD_ENV) down -v
	docker compose -f $(MAIN_COMPOSE) --env-file $(PROD_ENV) down -v
	docker compose -f $(STORE_COMPOSE) --env-file $(PROD_ENV) down -v
	@echo "$(YELLOW) 🛑 All Services are stopped 🛑 $(NC)"

run-core: ## Deploy core infrastructure (Traefik, etc.)
	@echo "$(GREEN)🚀 Deploying core infrastructure...$(NC)"
    docker compose -f $(CORE_COMPOSE) --env-file $(PROD_ENV) up -d
	@echo "$(GREEN)✅ Core infrastructure deployed$(NC)"

stop-core: ## Destroy core Infrastructure (traefik, etc.)
	@echo "${RED} Destroying current setup... ${NC}"
	docker compose -f ${CORE_COMPOSE} --env-file $(PROD_ENV) down -v
	@echo "${RED} DONE ${NC}"

run-main: ## Deploy main site
	@echo "$(GREEN)🚀 Deploying main site...$(NC)"
	docker compose -f $(MAIN_COMPOSE) --env-file $(PROD_ENV) up -d
	@echo "$(GREEN)✅ Main site deployed$(NC)"

stop-main: ## Destroy main site
	@echo "$(YELLOW) Removing main site... $(NC)"
	docker compose -f $(MAIN_COMPOSE) --env-file $(PROD_ENV) down -v
	@echo "$(YELLOW) Destruction complete $(NC)"

health-check: ## Check all services status
	@echo "$(GREEN)🔍 Checking core services...$(NC)"
	docker compose -f $(CORE_COMPOSE) ps
	@echo "$(GREEN)🔍 Checking main services...$(NC)"
	docker compose -f $(MAIN_COMPOSE) ps
	@echo "$(GREEN)🔍 Checking store services...$(NC)"
	docker compose -f $(STORE_COMPOSE) ps

restart-all: stop-all deploy-all ## Restart everything
