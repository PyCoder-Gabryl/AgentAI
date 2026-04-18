# =============================================================================
# newgithub.mk - Tworzenie repozytorium GitHub
# =============================================================================
# Ścieżka: MakeLIB/newgithub.mk
# Opis: Tworzy nowe publiczne repozytorium na GitHub i wypycha lokalny kod.
# Wymagania: Zainstalowany i zalogowany gh (GitHub CLI).
# =============================================================================

.PHONY: newgithub

newgithub: ## Utwórz repo na GitHub i wypchnij
	gh repo create AgentAI --public --source=. --push