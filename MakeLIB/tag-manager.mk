# =============================================================================
# tag-manager.mk - Zarządzanie dwujęzyczną bazą pojęć (PL <-> EN)
# =============================================================================
# Ścieżka: MakeLIB/tag-manager.mk
# Opis: Obsługa pliku data/tags.txt w formacie pl:en
# =============================================================================

TAGS_FILE := data/tags.txt

.PHONY: add-tags remove-tags show-tags tags-sort

add-tags: ## Dodaj tagi (t="pl=en" lub t="pl"). Przykład: make add-tags t="uczenie maszynowe"
	@clear
	@echo "📥 Uruchamiam: Menadżer Tagów (Dodawanie)..."
	@mkdir -p data
	@$(PYTHON) -m agentai.tag_manager add "$(t)"

remove-tags: ## Usuń tagi (t="pl" lub t="en"). Przykład: make remove-tags t="rust"
	@clear
	@echo "🔥 Uruchamiam: Menadżer Tagów (Usuwanie)..."
	@$(PYTHON) -m agentai.tag_manager remove "$(t)"

show-tags: ## Pokazuje pary PL <-> EN z bazy pojęć
	@clear
	@echo "📋 TWOJA BAZA POJĘĆ (PL <-> EN):"
	@echo "---------------------------------------------------"
	@if [ -f $(TAGS_FILE) ]; then \
		column -t -s ":" $(TAGS_FILE) | sed 's/^/   /'; \
	else \
		echo "   ⚠️ Baza jest pusta. Dodaj coś za pomocą make add-tags"; \
	fi
	@echo "---------------------------------------------------"

tags-sort: ## Sortuje i czyści plik tags.txt
	@clear
	@echo "🧹 Porządkowanie bazy tagów..."
	@if [ -f $(TAGS_FILE) ]; then \
		sed -i '/^[[:space:]]*$$/d' $(TAGS_FILE); \
		sort -t':' -k1 $(TAGS_FILE) -o $(TAGS_FILE); \
		echo "✅ Baza została posortowana alfabetycznie (PL)."; \
	else \
		echo "⚠️ Brak pliku do posortowania."; \
	fi
