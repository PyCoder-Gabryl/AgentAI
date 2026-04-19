# =============================================================================
# python.mk - Fundamenty środowiska
# =============================================================================
VENV     := .venv
PYTHON   := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip
export PYTHONPATH := src

.PHONY: agent-init agent-install agent-login pycharm-clean agent-full-clean

agent-init: ## Tworzenie venv
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip

agent-install: ## Instalacja zależności
	@$(PIP) install deep-translator duckdb playwright playwright-stealth beautifulsoup4 psutil
	@$(PYTHON) -m playwright install chromium
	@echo "✅ Biblioteki zainstalowane."

agent-login: ## Manualne logowanie do Medium (sesja)
	@clear
	@echo "🔑 Odświeżanie sesji Medium..."
	@$(PYTHON) -m agentai.lib.auth_generator

pycharm-clean: ## Usuwa śmieci Pythona (__pycache__, .pyc, .pytest_cache)
	@echo "🧹 Czyszczenie cache Pythona..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "✅ Cache wyczyszczony."

agent-full-clean: pycharm-clean ## Głębokie czyszczenie (śmieci IDE + dane Playwrighta)
	@echo "🔥 Głębokie sprzątanie..."
	@# Usuwamy logi i śmieci generowane przez przeglądarkę w data/
	@rm -rf data/user_data*
	@# Usuwamy potencjalne śmieci PyCharma (jeśli nie są w .gitignore)
	@rm -rf .idea/*.xml
	@echo "✅ Projekt lśni."
