# =============================================================================
# agent.mk - Operacje skanowania i scrapowania
# =============================================================================
# Używamy '=' zamiast ':=' aby opóźnić wykonanie komendy shell
DYNAMIC_TAGS_EN = $(shell [ -f $(TAGS_FILE) ] && cut -d':' -f2 $(TAGS_FILE) | tr '\n' ',' | sed 's/,$$//')

.PHONY: agent-batch agent-scan-core agent-scan-list agent-scan-url agent-search

agent-batch: ## Masowe skanowanie (tags="pl,en" date=2024 lim=50)
	@clear
	@echo "🚀 Uruchamiam: Batch Processor..."
	@$(PYTHON) -m agentai.lib.batch_processor "$(tags)" "$(date)" $(lim)

agent-scan-core: ## Automatyczny skan wszystkich tagów EN z bazy pojęć
	@clear
	@if [ -z "$(DYNAMIC_TAGS_EN)" ]; then \
		echo "⚠️ Błąd: Brak tagów w $(TAGS_FILE) lub plik nie istnieje."; \
		exit 1; \
	fi
	@echo "🔍 Skanowanie CORE dla: $(DYNAMIC_TAGS_EN)"
	@$(PYTHON) -m agentai.lib.batch_processor "$(DYNAMIC_TAGS_EN)" "" 50

agent-scan-list: ## Skanuje listę 'Reading List' z Medium
	@clear
	@$(PYTHON) -m agentai.core.scraper "" 1000

agent-scan-url: ## Pobiera pojedynczy URL (url="...")
	@clear
	@$(PYTHON) -m agentai.core.scraper "$(url)" 1

agent-search: ## Wyszukiwanie frazy (q="fraza" lim=20)
	@clear
	@$(PYTHON) -m agentai.core.scraper "$(q)" $(lim)
