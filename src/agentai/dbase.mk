# =============================================================================
# dbase.mk - Zarządzanie Wiedzą (DuckDB)
# =============================================================================
DB_PATH := data/agent_knowledge.db

db-init: ## Inicjalizuj tabele
	@$(PYTHON) -m agentai.database

db-stats: ## Statystyki ogólne
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	total = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	q_stat = 'SELECT status, count(*), round(count(*)*100.0/(SELECT count(*)+0.001 FROM articles), 1) \
	          FROM articles GROUP BY status'; \
	res = conn.execute(q_stat).fetchall(); \
	sources = conn.execute('SELECT source_account, count(*) FROM articles GROUP BY source_account \
	                        ORDER BY count(*) DESC LIMIT 5').fetchall(); \
	print('\n📊 --- STATUS WIEDZY ---'); \
	print(f'   Rekordy: {total}'); \
	[print(f'   {r[0]:<12}: {r[1]:<6} ({r[2]}%)') for r in res]; \
	print('\n📂 --- TOP ŹRÓDŁA ---'); \
	[print(f'   {r[0]:<20}: {r[1]}') for r in sources]"

db-tags: ## Ranking tagów
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	q_tags = 'SELECT topic, count(*), count(CASE WHEN status=\"pending\" THEN 1 END) \
	          FROM articles GROUP BY topic ORDER BY count(*) DESC'; \
	res = conn.execute(q_tags).fetchall(); \
	print('\n🏷️  --- RANKING TAGÓW ---'); \
	print(f'   {"TAG":<20} | {"ILOŚĆ":<5} | {"PENDING"}'); \
	[print(f'   {str(r[0]):<20} | {r[1]:<5} | {r[2]}') for r in res]"

db-history: ## Ostatnie misje
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	res = conn.execute('SELECT query_key, last_scanned, new_added FROM scan_history \
	                    ORDER BY last_scanned DESC LIMIT 10').fetchall(); \
	print('\n🧠 --- OSTATNIE MISJE ---'); \
	[print(f'   {r[0]:<25} | {str(r[1])[:16]} | Nowych: {r[2]}') for r in res]"

db-clean-trash: ## Sprzątanie śmieci
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	b = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	conn.execute(\"DELETE FROM articles WHERE length(title) < 10 OR url LIKE '%/followers' OR url LIKE '%/about'\"); \
	a = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	print(f'🧹 Usunięto: {b - a} rekordów.')"
