# =============================================================================
# agent.mk - Operacje i Skany (Tagi po przecinku)
# =============================================================================
TAGS_FILE := data/tags.txt
DYNAMIC_TAGS := $(shell [ -f $(TAGS_FILE) ] && cat $(TAGS_FILE) | tr '\n' ',' | sed 's/,$$//')

add-tags: ## Dodaj tagi (t="tag1, tag2")
	@mkdir -p data
	@echo "📥 Przetwarzanie..."
	@echo "$(t)" | tr ',' '\n' | \
		sed 's/^[[:space:]]*//;s/[[:space:]]*$$//' >> $(TAGS_FILE)
	@sort -u $(TAGS_FILE) -o $(TAGS_FILE)
	@echo "✅ Zaktualizowano listę w $(TAGS_FILE)"

agent-batch: ## Skanowanie wsadowe (tags="..." date="..." lim=...)
	@$(PYTHON) -m agentai.batch_processor "$(tags)" "$(date)" $(lim)

agent-scan-core: ## Automatyczny skan listy z tags.txt
	@echo "🔍 Start CORE scan dla: $(DYNAMIC_TAGS)"
	@$(PYTHON) -m agentai.batch_processor "$(DYNAMIC_TAGS)" "" 50

agent-scan-list: ## Reading List (limit 1000)
	@$(PYTHON) -m agentai.scraper "" 1000

agent-scan-url: ## Pojedynczy URL (url=...)
	@$(PYTHON) -m agentai.scraper "$(url)" 1

agent-search: ## Szukanie frazy (q=...)
	@$(PYTHON) -m agentai.scraper "$(q)" $(lim)
