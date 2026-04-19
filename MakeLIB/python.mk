# =============================================================================
# python.mk - Fundamenty środowiska
# =============================================================================
VENV     := .venv
PYTHON   := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip
export PYTHONPATH := src

# Dołączanie modułów tematycznych
include dbase.mk
include agent.mk

.PHONY: agent-init agent-install agent-login

agent-init: ## Inicjalizacja venv
	clear
	@echo "🔧 Tworzenie izolowanego środowiska..."
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip

agent-install: agent-init ## Instalacja bibliotek (AI + Scraper)
	clear
	@echo "🧠 Instalacja bibliotek..."
	@$(PIP) install llama-index-llms-ollama \
		llama-index-embeddings-huggingface \
		chromadb playwright duckdb beautifulsoup4 \
		psutil streamlit playwright-stealth
	@$(PYTHON) -m playwright install chromium
	@echo "✅ System gotowy."

agent-login: ## Odśwież sesję Medium
	@$(PYTHON) -m agentai.auth_generator
