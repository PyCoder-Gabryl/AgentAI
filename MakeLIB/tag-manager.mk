# =============================================================================
# tag-manager.mk - Zarządzanie dwujęzyczną bazą pojęć (PL <-> EN)
# =============================================================================
TAGS_FILE  := data/tags.txt
BACKUP_FILE := data/tags.txt.bak

.PHONY: add-tags remove-tags show-tags tags-sort tags-backup

tags-backup: ## Tworzy kopię zapasową pliku tagów
	@if [ -f $(TAGS_FILE) ]; then \
		cp $(TAGS_FILE) $(BACKUP_FILE); \
		echo "💾 Backup utworzony: $(BACKUP_FILE)"; \
	fi

add-tags: tags-backup ## Dodaj tagi (make add-tags t="pojęcie")
	@clear
	@if [ -z "$(t)" ]; then \
		echo "❌ Błąd: Musisz podać tagi. Użyj: make add-tags t=\"pl=en\""; \
		exit 1; \
	fi
	@echo "📥 Uruchamiam: Menadżer Tagów (Dodawanie)..."
	@mkdir -p data
	@$(PYTHON) -m agentai.lib.tag_manager add "$(t)"
	@$(MAKE) tags-sort

remove-tags: tags-backup ## Usuń tagi (make remove-tags t="pojęcie")
	@clear
	@if [ -z "$(t)" ]; then \
		echo "❌ Błąd: Musisz podać co usunąć. Użyj: make remove-tags t=\"pojęcie\""; \
		exit 1; \
	fi
	@echo "🔥 Uruchamiam: Menadżer Tagów (Usuwanie)..."
	@$(PYTHON) -m agentai.lib.tag_manager remove "$(t)"
	@$(MAKE) tags-sort

show-tags: ## Pokazuje pary PL <-> EN z bazy pojęć
	@clear
	@echo "📋 TWOJA BAZA POJĘĆ (PL <-> EN):"
	@echo "---------------------------------------------------"
	@if [ -f $(TAGS_FILE) ]; then \
		column -t -s ":" $(TAGS_FILE) | sed 's/^/   /'; \
	else \
		echo "   ⚠️ Baza jest pusta. Użyj: make add-tags t=\"pojęcie\""; \
	fi
	@echo "---------------------------------------------------"

tags-sort: ## Czyści puste linie i sortuje bazę
	@if [ -f $(TAGS_FILE) ]; then \
		# Usuwanie pustych linii (kompatybilne z macOS/Linux) \
		sed -i.tmp '/^[[:space:]]*$$/d' $(TAGS_FILE) && rm $(TAGS_FILE).tmp; \
		# Sortowanie unikalne \
		sort -u -t':' -k1 $(TAGS_FILE) -o $(TAGS_FILE); \
		echo "🧹 Baza posortowana i wyczyszczona."; \
	fi
