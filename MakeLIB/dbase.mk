# =============================================================================
# dbase.mk - Zarządzanie Bazą Danych DuckDB
# =============================================================================
DB_PATH := data/agent_knowledge.db

.PHONY: db-init db-stats db-tags db-history db-clean-trash

db-init: ## Inicjalizacja struktur bazy danych
	@echo "🛠️ Inicjalizacja bazy..."
	@$(PYTHON) -m agentai.core.database

db-stats: ## Statystyki bazy danych (Naprawiony Lock)
	@clear
	@echo "📊 Statystyki wiedzy..."
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)', read_only=True, config={'allow_unsigned_extensions': 'true'}); \
	sql = 'SELECT count(*) FROM articles'; \
	res = conn.execute(sql).fetchone(); \
	print(f'\n📂 Całkowita liczba artykułów: {res[0]}'); \
	conn.close()"

db-tags: ## Ranking tagów (Naprawiony Lock)
	@clear
	@echo "🏷️ Pobieranie rankingu tagów..."
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)', read_only=True, config={'allow_unsigned_extensions': 'true'}); \
	sql = 'SELECT topic, count(*) FROM articles GROUP BY topic ORDER BY count(*) DESC'; \
	res = conn.execute(sql).fetchall(); \
	print('\n🏷️  RANKING TAGÓW:'); \
	[print(f'   {str(r[0]):<20} | {r[1]} art.') for r in res]; \
	conn.close()"

db-clean-trash: ## Oznacza śmieciowe linki (Rozbite linie)
	@clear
	@echo "🧹 Analiza śmieci..."
	@$(PYTHON) -c "from agentai.core.database import AgentDatabase; \
	db = AgentDatabase(); \
	count = db.sanitize_database(); \
	print(f'✅ Zablokowano {count} linków.')"
