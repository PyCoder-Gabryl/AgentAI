# =============================================================================
# ollama.mk - Zarządzanie lokalnym mózgiem AI (Ollama)
# =============================================================================
# Ścieżka: MakeLIB/ollama.mk
# Opis: Obsługa serwera LLM, monitorowanie modeli i zasobów.
# =============================================================================

.PHONY: ollama-start ollama-stop ollama-status ollama-list ollama-clean

ollama-start: ## Uruchamia serwer Ollama w tle z optymalizacją pod Agenta
	@clear
	@echo "🚀 Uruchamianie serwera Ollama..."
	@if pgrep -x "ollama" > /dev/null; then \
		echo "⚠️ Ollama już działa."; \
	else \
		export OLLAMA_KEEP_ALIVE="24h"; \
		export OLLAMA_NUM_PARALLEL=2; \
		nohup ollama serve > /dev/null 2>&1 & \
		sleep 2; \
		echo "✅ Serwer wystartował (Keep-alive: 24h, Parallel: 2)."; \
	fi

ollama-stop: ## Zatrzymuje serwer Ollama
	@clear
	@echo "🛑 Zatrzymywanie serwera Ollama..."
	@pkill -x "ollama" || echo "⚠️ Serwer nie był uruchomiony."
	@echo "✅ Zatrzymano."

ollama-status: ## Pokazuje szczegółowy status: procesy, modele i zużycie RAM
	@clear
	@echo "🧠 --- STATUS MÓZGU AI (OLLAMA) ---"
	@if pgrep -x "ollama" > /dev/null; then \
		echo "Status: [AKTYWNY]"; \
		echo "-----------------------------------"; \
		echo "📊 ZUŻYCIE ZASOBÓW:"; \
		ps -o %cpu,%mem,rss -p $$(pgrep -x "ollama") | awk 'NR==1{print "   CPU%  MEM%  RAM_RSS"}; NR==2{print "   "$$1"%  "$$2"%  "$$3/1024" MB"}'; \
		echo ""; \
		echo "🚀 MODELE W PAMIĘCI (Active):"; \
		curl -s http://localhost:11434/api/ps | jq -r '.models[] | "   - " + .name + " (" + (.size/1073741824 | strftime("%0.2f")) + " GB)"' 2>/dev/null || echo "   Brak załadowanych modeli."; \
	else \
		echo "Status: [NIEAKTYWNY]"; \
	fi
	@echo "-----------------------------------"

ollama-list: ## Wyświetla listę wszystkich pobranych modeli
	@clear
	@echo "📦 --- DOSTĘPNE MODELE LOKALNE ---"
	@ollama list
	@echo "-----------------------------------"

ollama-pull: ## Pobiera domyślne modele Agenta (llama3, nomic-embed-text)
	@clear
	@echo "📥 Pobieranie modeli bazowych..."
	@ollama pull llama3
	@ollama pull nomic-embed-text
	@echo "✅ Modele gotowe do pracy."

ollama-clean: ## Czyści pamięć RAM z nieużywanych modeli
	@clear
	@echo "🧹 Czyszczenie pamięci modeli..."
	@curl -X POST http://localhost:11434/api/generate -d '{"model": "llama3", "keep_alive": 0}' > /dev/null
	@echo "✅ Modele wyładowane z RAM."
