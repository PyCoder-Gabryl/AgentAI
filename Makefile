#!/usr/bin/env make
# =============================================================================
# Makefile - Główny plik konfiguracyjny projektu Knowledge Weaver
# =============================================================================
# Opis: Główny plik Makefile includujący wszystkie moduły z katalogu MakeLIB.
#       Użyj `make help` aby zobaczyć dostępne polecenia.
# =============================================================================

SHELL := /bin/zsh
.SHELLFLAGS := -e

.DELETE_ON_ERROR:
.ONESHELL:
.SORT:

.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Help - Wyświetla dostępne polecenia z opisami
# -----------------------------------------------------------------------------
.PHONY: help

help:
	@awk '/^[a-zA-Z_-]+:.*##/ && !seen[$$1]++ {sub(/MakeLIB\//,""); sub(/\.mk/,""); printf "\033[36m%-15s\033[0m %s\n", $$1, substr($$0, index($$0,$$3))}' MakeLIB/*.mk | sort

# -----------------------------------------------------------------------------
# Includowanie modułów MakeLIB
# -----------------------------------------------------------------------------
include MakeLIB/cleangit.mk
include MakeLIB/newgithub.mk
include MakeLIB/ollama.mk