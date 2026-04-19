# =============================================================================
# dbase.mk - Zarządzanie Bazą Danych DuckDB
# =============================================================================
DB_PATH := data/agent_knowledge.db

.PHONY: db-init db-stats db-tags db-history db-clean-trash

db-init: ## Inicjalizacja struktur bazy danych
	@echo "🛠️ Inicjalizacja bazy..."
	@$(PYTHON) -m agentai.core.database

db-stats: ## Statystyki bazy danych
	@clear
	@echo "📊 Statystyki wiedzy..."
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	total = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	print(f'\n📂 Całkowita liczba artykułów: {total}'); \
	conn.close()"

db-tags: ## Ranking tagów pobrany z bazy danych
	@clear
	@echo "🏷️ Pobieranie rankingu tagów z bazy..."
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	res = conn.execute('SELECT topic, count(*) FROM articles GROUP BY topic ORDER BY count(*) DESC').fetchall(); \
	print('\n🏷️  RANKING TAGÓW W BAZIE:'); \
	[print(f'   {str(r[0]):<20} | {r[1]} art.') for r in res]; \
	conn.close()"

db-clean-trash: ## Usuwa śmieciowe linki z bazy
	@clear
	@echo "🧹 Czyszczenie bazy..."
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	conn.execute(\"DELETE FROM articles WHERE url LIKE '%/followers' OR length(title) < 5\"); \
	conn.close(); print('✅ Baza wyczyszczona.')"
