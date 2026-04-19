# =============================================================================
# ollama.mk - Zarządzanie lokalnym mózgiem AI (Ollama)
# =============================================================================

.PHONY: ollama-start ollama-stop ollama-status ollama-list ollama-pull ollama-clean

ollama-start: ## Uruchamia serwer Ollama w tle
	@if pgrep -x "ollama" > /dev/null; then \
		echo "⚠️ Ollama już działa."; \
	else \
		echo "🚀 Uruchamianie serwera Ollama..."; \
		export OLLAMA_KEEP_ALIVE="24h"; \
		export OLLAMA_NUM_PARALLEL=2; \
		nohup ollama serve > /dev/null 2>&1 & \
		sleep 4; \
		echo "✅ Serwer wystartował."; \
	fi

ollama-stop: ## Zatrzymuje serwer Ollama
	@echo "🛑 Zatrzymywanie serwera Ollama..."
	@pkill -x "ollama" && echo "✅ Zatrzymano." || \
		echo "⚠️ Serwer nie był uruchomiony."

ollama-list: ## Wyświetla listę modeli (Auto-start/stop)
	@clear
	@echo "📦 --- DOSTĘPNE MODELE LOKALNE ---"
	@WAS_RUNNING=1; \
	if ! pgrep -x "ollama" > /dev/null; then \
		WAS_RUNNING=0; \
		$(MAKE) ollama-start > /dev/null; \
	fi; \
	ollama list; \
	echo "-----------------------------------"; \
	if [ $$WAS_RUNNING -eq 0 ]; then \
		echo "🧹 Samoczynne sprzątanie: zatrzymuję serwer..."; \
		$(MAKE) ollama-stop > /dev/null; \
	fi

ollama-pull: ## Pobiera/Aktualizuje modele (Auto-start/stop)
	@clear
	@echo "📥 --- AKTUALIZACJA MODELI AGENTA ---"
	@WAS_RUNNING=1; \
	if ! pgrep -x "ollama" > /dev/null; then \
		WAS_RUNNING=0; \
		$(MAKE) ollama-start > /dev/null; \
	fi; \
	echo "📥 Pobieranie: Llama3..."; \
	ollama pull llama3; \
	echo "📥 Pobieranie: Nomic Embed Text..."; \
	ollama pull nomic-embed-text; \
	echo "-----------------------------------"; \
	if [ $$WAS_RUNNING -eq 0 ]; then \
		echo "🧹 Samoczynne sprzątanie: zatrzymuję serwer..."; \
		$(MAKE) ollama-stop > /dev/null; \
	fi; \
	echo "✅ Modele są aktualne."

ollama-status: ## Status procesów i modeli
	@clear
	@echo "🧠 --- STATUS MÓZGU AI (OLLAMA) ---"
	@if pgrep -x "ollama" > /dev/null; then \
		echo "Status: [AKTYWNY]"; \
		echo "-----------------------------------"; \
		ps -o %cpu,%mem,rss -p $$(pgrep -x "ollama") | \
			awk 'NR==1{print "   CPU%  MEM%  RAM_RSS"}; \
			     NR==2{print "   "$$1"%  "$$2"%  "$$3/1024" MB"}'; \
		echo ""; \
		echo "🚀 MODELE W PAMIĘCI:"; \
		curl -s http://localhost:11434/api/ps | jq -r '.models[] | \
			"   - " + .name + " (" + \
			(.size/1073741824 | strftime("%0.2f")) + " GB)"' \
			2>/dev/null || echo "   Brak załadowanych modeli."; \
	else \
		echo "Status: [NIEAKTYWNY]"; \
	fi
	@echo "-----------------------------------"

ollama-clean: ## Wyładowuje modele z RAM
	@echo "🧹 Czyszczenie RAM z modeli..."
	@curl -s -X POST http://localhost:11434/api/generate \
		-d '{"model": "llama3", "keep_alive": 0}' > /dev/null
	@echo "✅ Modele wyładowane."
