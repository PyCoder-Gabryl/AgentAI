# =============================================================================
# agent.mk - Operacje skanowania i scrapowania
# =============================================================================
# Ścieżka: MakeLIB/agent.mk
# Wymaga: tag-manager.mk (dla definicji TAGS_FILE)
# =============================================================================

# Pobiera tylko angielskie człony (drugi kolumna po dwukropku) do skanowania
DYNAMIC_TAGS_EN := $(shell [ -f $(TAGS_FILE) ] && cut -d':' -f2 $(TAGS_FILE) | tr '\n' ',' | sed 's/,$$//')

.PHONY: agent-batch agent-scan-core agent-scan-list agent-scan-url agent-search

agent-batch: ## Masowe skanowanie (tags="pl,en" date=2024 lim=50)
	@clear
	@echo "🚀 Uruchamiam: Batch Processor dla tagów: $(tags)"
	@$(PYTHON) -m agentai.batch_processor "$(tags)" "$(date)" $(lim)

agent-scan-core: ## Automatyczny skan wszystkich tagów EN z bazy pojęć
	@clear
	@echo "🔍 Uruchamiam: Skanowanie CORE (wszystkie tagi z bazy)..."
	@echo "Tags: $(DYNAMIC_TAGS_EN)"
	@$(PYTHON) -m agentai.batch_processor "$(DYNAMIC_TAGS_EN)" "" 50

agent-scan-list: ## Skanuje Twoją listę 'Reading List' z Medium
	@clear
	@echo "📚 Uruchamiam: Skanowanie Reading List (Medium)..."
	@$(PYTHON) -m agentai.scraper "" 1000

agent-scan-url: ## Skanuje pojedynczy artykuł (url="...")
	@clear
	@echo "🔗 Uruchamiam: Pobieranie pojedynczego adresu URL..."
	@$(PYTHON) -m agentai.scraper "$(url)" 1

agent-search: ## Szybkie wyszukiwanie frazy (q="fraza" lim=20)
	@clear
	@echo "🔎 Uruchamiam: Wyszukiwanie frazy '$(q)'..."
	@$(PYTHON) -m agentai.scraper "$(q)" $(lim)
