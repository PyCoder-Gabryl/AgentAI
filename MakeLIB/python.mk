# =============================================================================
# python.mk - Środowisko operacyjne Agenta AI (v2 - Multi-Tool)
# =============================================================================

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
# Ustawienie PYTHONPATH, aby moduły z src/agentai były widoczne
export PYTHONPATH := src

.PHONY: agent-init agent-install agent-run agent-login db-init db-show db-stats db-trends

# --- KONFIGURACJA ŚRODOWISKA ---

agent-init: ## Inicjalizacja środowiska dla Agenta
	clear
	@echo "Tworzenie izolowanego środowiska..."
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip

agent-install: agent-init ## Instalacja "mózgu" Agenta i jego narzędzi
	clear
	@echo "Instalacja bibliotek AI i Scrapera..."
	@$(PIP) install llama-index-llms-ollama llama-index-embeddings-huggingface \
	   chromadb playwright duckdb beautifulsoup4 psutil streamlit playwright-stealth
	@$(PYTHON) -m playwright install chromium
	@echo "System gotowy do pracy."

agent-login: ## Odśwież sesję Medium (wygeneruj auth.json)
	clear
	@$(PYTHON) -m agentai.auth_generator

db-init: ## Inicjalizuj bazę danych DuckDB
	clear
	@$(PYTHON) -m agentai.database

# --- POLECENIA SKANOWANIA (ZGODNE Z ROADMAPĄ) ---

agent-scan-list: ## Skanuje domyślną listę (Reading List) - limit 1000
	clear
	@$(PYTHON) -m agentai.scraper "" 1000

agent-scan-url: ## Skanuje konkretny URL. Przykład: make agent-scan-url url=https://medium.com/p/12345
	clear
	@$(PYTHON) -m agentai.scraper "$(url)" 1

agent-search: ## Szuka frazy i zbiera wyniki. Przykład: make agent-search q="python agents" lim=100
	clear
	@$(PYTHON) -m agentai.scraper "$(q)" $(lim)

agent-scan-date: ## Skanuj tag z datą (YYYY-MM-DD/YYYY-MM/YYYY). Przykład: make agent-scan-date tag=python date=2024-04-19
	clear
	@$(PYTHON) -m agentai.scraper "$(tag):$(date)" 1000

# --- NARZĘDZIA ANALITYCZNE I BAZODANOWE ---

# --- NARZĘDZIA ANALITYCZNE I BAZODANOWE ---

db-stats: ## Pokaż rozszerzone statystyki bazy
	clear
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('data/agent_knowledge.db'); \
	total = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	res = conn.execute('SELECT status, count(*), round(count(*)*100.0/(SELECT count(*) FROM articles), 1) FROM articles GROUP BY status').fetchall(); \
	sources = conn.execute('SELECT source, count(*) FROM articles GROUP BY source ORDER BY count(*) DESC LIMIT 5').fetchall(); \
	print('\n📊 --- STATUS WIEDZY AGENTA ---'); \
	print(f'   Łącznie rekordów: {total}'); \
	print('-----------------------------------'); \
	[print(f'   {r[0]:<12}: {r[1]:<6} ({r[2]}%)') for r in res]; \
	print('\n📂 --- TOP ŹRÓDŁA ---'); \
	[print(f'   {r[0]:<20}: {r[1]}') for r in sources]; \
	print('-----------------------------------')"

db-clean-trash: ## Czyści śmieci i raportuje co usunięto
	clear
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('data/agent_knowledge.db'); \
	before = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	# Usunięcie systemowych linków Medium i krótkich śmieci \
	conn.execute(\"DELETE FROM articles WHERE length(title) < 10 \
	OR url LIKE '%/followers' OR url LIKE '%/about' \
	OR title IN ('Status', 'Careers', 'Privacy', 'Text to speech', 'People', 'Publications', 'Topics')\"); \
	after = conn.execute('SELECT count(*) FROM articles').fetchone()[0]; \
	removed = before - after; \
	print(f'\n🧹 SPRZĄTANIE ZAKOŃCZONE'); \
	print(f'   Usunięto rekordów : {removed}'); \
	print(f'   Pozostało w bazie : {after}'); \
	print(f'   Zredukowano bazę o: {round((removed/before)*100, 2) if before > 0 else 0}%'); \
	print('-----------------------------------')"

db-trends: ## Pokaż przyrost wiedzy w czasie (ile artykułów dodano danego dnia)
	clear
	@$(PYTHON) -c "import duckdb; \
	conn = duckdb.connect('data/agent_knowledge.db'); \
	res = conn.execute(\"SELECT date(created_at) as d, count(*) FROM articles GROUP BY d ORDER BY d DESC LIMIT 10\").fetchall(); \
	print('\n📈 --- TRENDY PRZYROSTU WIEDZY ---'); \
	[print(f'   {str(r[0])}: {r[1]} nowych') for r in res]; \
	print('-----------------------------------')"

# --- ZARZĄDZANIE AGENTEM (ZAPOWIEDŹ) ---

agent-sync: ## Synchronizacja bazy SQL z Sejfem Obsidian (Roadmap Faza 3)
	@echo "🔄 Rozpoczynam synchronizację z Obsidianem..."
	@echo "⚠️ Funkcja w trakcie implementacji (zobacz ROADMAP.md)."

CORE_TAGS := python uv hatch rust makefile zsh shell bash sh

agent-scan-core: ## Skanuje wszystkie główne tagi jeden po drugim
	@for tag in $(CORE_TAGS); do \
		echo "🔍 Rozpoczynam skanowanie tagu: $$tag"; \
		$(PYTHON) -m agentai.scraper "$$tag" 50; \
	done

# Przykład: make agent-batch tags="python rust" date=2023 lim=50
agent-batch: ## Masowe skanowanie: tags="t1 t2" [date=YYYY-MM] [lim=100]
	clear
	@$(PYTHON) -m agentai.batch_processor "$(tags)" "$(date)" $(lim)
