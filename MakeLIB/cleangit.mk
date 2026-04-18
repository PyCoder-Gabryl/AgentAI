# =============================================================================
# cleangit.mk - Czyszczenie śledzenia Git
# =============================================================================
# Ścieżka: MakeLIB/cleangit.mk
# Opis: Usuwa katalog .idea ze śledzenia Git i commituje zmianę.
# =============================================================================

.PHONY: cleangit

cleangit: ## Usuń .idea ze śledzenia git
	git rm --cached -rf .idea/
	git commit -m "Usuń .idea ze śledzenia git"