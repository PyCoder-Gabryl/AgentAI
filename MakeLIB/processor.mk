# =============================================================================
# processor.mk - Procesowanie treści przez AI i Scraping
# =============================================================================

.PHONY: run-enricher

run-enricher: ## Uruchamia proces wzbogacania artykułów (AI + Scraping)
	@clear
	@echo "🤖 Uruchamiam Enricher AI..."
	hatch run python -m agentai.workers.enricher
