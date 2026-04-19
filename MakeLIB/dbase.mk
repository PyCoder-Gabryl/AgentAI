# =============================================================================
# dbase.mk - Zarządzanie Bazą Danych DuckDB
# =============================================================================
DB_PATH := data/agent_knowledge.db

.PHONY: db-init db-stats db-tags db-history db-clean-trash

db-init: ## Inicjalizuj/Napraw tabele bazy danych
	@clear
	@echo "🛠️ Inicjalizacja bazy danych..."
	@$(PYTHON) -m agentai.database

db-stats: ## Wyświetla główne statystyki wiedzy i top źródła
	@clear
	@echo "📊 Pobieranie statystyk bazy danych..."
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	total = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	q_stat = 'SELECT status, count(*), round(count(*)*100.0/(SELECT count(*)+0.001 FROM articles), 1) FROM articles GROUP BY status'; \
	res = conn.execute(q_stat).fetchall(); \
	sources = conn.execute('SELECT source_account, count(*) FROM articles GROUP BY source_account ORDER BY count(*) DESC LIMIT 5').fetchall(); \
	print('\n📊 --- STATUS WIEDZY AGENTA ---'); \
	print(f'   Rekordy całkowite: {total}'); \
	print('-----------------------------------'); \
	[print(f'   {r[0]:<12}: {r[1]:<6} ({r[2]}%)') for r in res]; \
	print('\n📂 --- TOP KONTA/ŹRÓDŁA ---'); \
	[print(f'   {r[0]:<20}: {r[1]}') for r in sources]; \
	print('-----------------------------------')"

db-tags: ## Ranking tagów na podstawie liczby artykułów w bazie
	@clear
	@echo "🏷️ Generowanie rankingu tagów z bazy..."
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	q_tags = 'SELECT topic, count(*), count(CASE WHEN status=\"pending\" THEN 1 END) FROM articles GROUP BY topic ORDER BY count(*) DESC'; \
	res = conn.execute(q_tags).fetchall(); \
	print('\n🏷️  --- RANKING TAGÓW W BAZIE ---'); \
	print(f'   {"TAG":<20} | {"ARTYKUŁY":<8} | {"DO PRZETWORZENIA"}'); \
	print('---------------------------------------------------'); \
	[print(f'   {str(r[0]):<20} | {r[1]:<8} | {r[2]}') for r in res]"

db-history: ## Wyświetla 10 ostatnich misji skanowania
	@clear
	@echo "🧠 Odczytywanie pamięci operacyjnej..."
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	res = conn.execute('SELECT query_key, last_scanned, new_added FROM scan_history ORDER BY last_scanned DESC LIMIT 10').fetchall(); \
	print('\n🧠 --- HISTORIA OSTATNICH MISJI ---'); \
	print(f'   {"KLUCZ ZAPYTANIA":<25} | {"DATA SKANU":<16} | {"DODANO"}'); \
	print('---------------------------------------------------'); \
	[print(f'   {r[0]:<25} | {str(r[1])[:16]} | {r[2]}') for r in res]"

db-clean-trash: ## Usuwa duplikaty, krótkie tytuły i śmieci systemowe
	@clear
	@echo "🧹 Rozpoczynam sprzątanie bazy danych..."
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('$(DB_PATH)'); \
	b = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	conn.execute(\"DELETE FROM articles WHERE length(title) < 10 OR url LIKE '%/followers' OR url LIKE '%/about'\"); \
	a = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	print(f'✅ Sprzątanie zakończone. Usunięto {b - a} niepotrzebnych wpisów.')"
