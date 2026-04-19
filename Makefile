# =============================================================================
# Makefile - Główny plik konfiguracyjny projektu Knowledge Weaver
# =============================================================================
SHELL := /bin/zsh
.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Includowanie modułów MakeLIB
# -----------------------------------------------------------------------------
# Używamy -include, aby make nie wywalił błędu, jeśli katalog jest pusty
-include MakeLIB/*.mk

# -----------------------------------------------------------------------------
# Help - Wyświetla dostępne polecenia
# -----------------------------------------------------------------------------
.PHONY: help

help: ## Wyświetla dostępne polecenia z opisami
	@echo "Dostępne polecenia:"
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Przykładowe zadanie w głównym pliku
init: ## Inicjalizacja środowiska projektowego
	@echo "Inicjalizacja..."
