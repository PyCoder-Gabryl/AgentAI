# =============================================================================
# Makefile - Główny Zarządca Systemu
# =============================================================================
SHELL := /bin/zsh
.DEFAULT_GOAL := help

# Import modułów - ważne, aby pliki .mk były w katalogu MakeLIB
-include MakeLIB/*.mk

.PHONY: help init tree

help: ## Wyświetla pomoc pogrupowaną sekcjami
	@clear
	@echo "🤖 AGENT AI - PANEL STEROWANIA"
	@echo "============================================================"
	@for file in $(MAKEFILE_LIST); do \
		if grep -q "##" $$file; then \
			printf "\n\033[1;33m📂 MODUŁ: %-30s\033[0m\n" $$(basename $$file); \
			grep -E '^[a-zA-Z_-]+:.*?## .*$$' $$file | \
			awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'; \
		fi; \
	done
	@echo "\n============================================================"

init: ## Pełna inicjalizacja projektu
	@clear
	@$(MAKE) agent-init
	@$(MAKE) agent-install
	@$(MAKE) db-init

tree: ## Pokazuje strukturę projektu (bez śmieci i cache)
	@clear
	@echo "📂 STRUKTURA PROJEKTU (Knowledge Weaver):"
	@tree -I "__pycache__|.venv|.git|.pytest_cache|*.egg-info|user_data*|GrShaderCache|ShaderCache" \
		  --dirsfirst \
		  -F
