# =============================================================================
# ollama.mk - Zarządzanie Ollama
# =============================================================================
# Ścieżka: MakeLIB/ollama.mk
# Opis: Polecenia do zarządzania instalacją i usługą Ollama (LLM runner).
# Wymagania: Zainstalowany i skonfigurowany Homebrew.
# =============================================================================

.PHONY: ollama-upgrade ollama-start ollama-stop

ollama-upgrade: ## Sprawdź/instaluj/zaktualizuj Ollama
	@if ! command -v ollama &> /dev/null; then \
		echo "Ollama nie jest zainstalowana. Instaluję..."; \
		brew install ollama; \
	else \
		echo "Ollama jest zainstalowana."; \
		brew update && brew upgrade ollama; \
	fi

ollama-start: ## Uruchom usługę Ollama
	launchctl start com.ollama.launcher

ollama-stop: ## Zatrzymaj usługę Ollama
	launchctl stop com.ollama.launcher