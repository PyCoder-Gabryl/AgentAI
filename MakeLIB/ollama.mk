# =============================================================================
# ollama.mk - Zarządzanie Ollama
# =============================================================================
# Ścieżka: MakeLIB/ollama.mk
# Opis: Polecenia do zarządzania instalacją i usługą Ollama (LLM runner).
# Wymagania: Zainstalowany i skonfigurowany Homebrew.
# =============================================================================

.PHONY: ollama-upgrade ollama-start ollama-stop ollama-status ollama-pull

ollama-upgrade: ## Sprawdź/instaluj/zaktualizuj Ollama
	@if ! command -v ollama &> /dev/null; then \
		echo "Ollama nie jest zainstalowana. Instaluję przez brew..."; \
		brew install ollama; \
	else \
		echo "Ollama jest zainstalowana. Aktualizuję..."; \
		brew upgrade ollama; \
	fi

ollama-start: ## Uruchom serwer z własną konfiguracją
	@echo "Uruchamianie serwera Ollama z optymalizacją pod Agenta..."
	@if pgrep -x "ollama" > /dev/null; then \
		echo "Ollama już działa."; \
	else \
		export OLLAMA_KEEP_ALIVE="24h"; \
		export OLLAMA_NUM_PARALLEL=2; \
		export OLLAMA_DEBUG=1; \
		nohup ollama serve > /dev/null 2>&1 & \
		sleep 2; \
		echo "Serwer wystartował (Keep-alive: 24h, Parallel: 2, Debug: ON)."; \
	fi

ollama-stop: ## Zatrzymaj serwer Ollama
	@echo "Zatrzymywanie serwera Ollama..."
	@killall ollama 2>/dev/null || echo "Proces Ollama nie był uruchomiony."

ollama-status: ## Szczegółowy status serwera, modeli i zasobów
	@echo "--- STATUS PROCESU ---"
	@if pgrep -x "ollama" > /dev/null; then \
		echo "Proces Ollama: [AKTYWNY]"; \
		echo "PID: $$(pgrep -x "ollama")"; \
		echo "Port: $$(lsof -Pi :11434 -sTCP:LISTEN -t >/dev/null && echo "11434 (Słucha)" || echo "Brak nasłuchu")"; \
		echo ""; \
		echo "--- ZASOBY SYSTEMOWE (M1) ---"; \
		ps -ro %cpu,%mem,rss -p $$(pgrep -x "ollama") | awk 'NR==1{print "CPU%  MEM%  RES_RAM"}; NR==2{print $$1"  "$$2"  "$$3/1024" MB"}'; \
		echo ""; \
		echo "--- AKTUALNIE ZAŁADOWANE MODELE ---"; \
		curl -s http://localhost:11434/api/ps | jq -r '.models[] | "Model: " + .name + " | Rozmiar: " + (.size/1073741824 | strftime("%0.2f")) + " GB | Kontekst: " + (.details.parameter_size)"' 2>/dev/null || echo "Brak aktywnego modelu w pamięci RAM."; \
		echo ""; \
		echo "--- LISTA POBRANYCH PLIKÓW ---"; \
		ollama list; \
	else \
		echo "Proces Ollama: [NIEAKTYWNY]"; \
	fi

ollama-update-all: ## Aktualizuj absolutnie wszystkie pobrane modele (auto-start)
	@if ! pgrep -x "ollama" > /dev/null; then \
		echo "Serwer nie działa. Uruchamiam tymczasowo..."; \
		nohup ollama serve > /dev/null 2>&1 & \
		sleep 5; \
	fi
	@echo "Aktualizacja wszystkich lokalnych modeli..."
	@# Pobieramy listę, usuwamy nagłówek i czyścimy puste linie
	@models=$$(ollama list | tail -n +2 | awk '{print $$1}' | grep .); \
	for model in $$models; do \
		echo ">>> Aktualizuję: $$model"; \
		ollama pull $$model; \
	done

ollama-logs: ## Śledź logi serwera Ollama w czasie rzeczywistym
	@echo "Podgląd logów serwera (Ctrl+C aby zakończyć)..."
	@if [ -f ~/.ollama/logs/server.log ]; then \
		tail -f ~/.ollama/logs/server.log; \
	else \
		echo "Błąd: Plik logów nie istnieje. Uruchom najpierw serwer."; \
	fi

ollama-logs-clear: ## Wyczyść plik logów
	@echo "Czyszczenie logów..."
	@rm -f ~/.ollama/logs/server.log && echo "Logi usunięte."
