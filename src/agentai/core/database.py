# =============================================================================
# AgentAI - Core Database Module
# =============================================================================
import os

import duckdb


class AgentDatabase:
	def __init__(self, db_path='data/agent_knowledge.db'):
		os.makedirs(os.path.dirname(db_path), exist_ok=True)
		self.conn = duckdb.connect(db_path)
		self._setup_tables()
		self._migrate_tables()  # Automatyczne dodawanie nowych kolumn

	def _setup_tables(self):
		"""Inicjalizacja podstawowej struktury tabel."""
		self.conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                url VARCHAR PRIMARY KEY,
                title VARCHAR,
                topic VARCHAR,
                priority INTEGER,
                status VARCHAR,
                content_summary TEXT,
                source_account VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
		self.conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                query_key VARCHAR PRIMARY KEY, 
                last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_found INTEGER,
                new_added INTEGER
            )
        """)

	def _migrate_tables(self):
		"""Dodaje nowe kolumny, jeśli jeszcze nie istnieją (Bezpieczna Migracja)."""
		# Pobieramy listę kolumn w tabeli articles
		columns_info = self.conn.execute("PRAGMA table_info('articles')").fetchall()
		column_names = [col[1] for col in columns_info]

		# 1. Kolumna na polski tytuł
		if 'title_pl' not in column_names:
			print("🔧 Migracja: Dodawanie kolumny 'title_pl'...")
			self.conn.execute('ALTER TABLE articles ADD COLUMN title_pl VARCHAR')

		# 2. Kolumna na punktowe streszczenie po polsku
		if 'summary_pl' not in column_names:
			print("🔧 Migracja: Dodawanie kolumny 'summary_pl'...")
			self.conn.execute('ALTER TABLE articles ADD COLUMN summary_pl TEXT')

	def add_article(self, url, title, topic, priority, source='main'):
		try:
			# Używamy jawnie nazw kolumn, aby uniknąć błędów po migracji
			self.conn.execute(
				'INSERT INTO articles (url, title, topic, priority, status, source_account) '
				"VALUES (?, ?, ?, ?, 'pending', ?)",
				[url, title, topic, priority, source],
			)
			return True
		except duckdb.ConstraintException:
			return False

	def is_already_scanned(self, query_key):
		res = self.conn.execute(
			"SELECT query_key FROM scan_history WHERE query_key = ? AND last_scanned > now() - interval '30 days'",
			[query_key],
		).fetchone()
		return res is not None

	def mark_as_scanned(self, query_key, total_found, new_added):
		self.conn.execute(
			'INSERT OR REPLACE INTO scan_history (query_key, last_scanned, total_found, new_added) '
			'VALUES (?, CURRENT_TIMESTAMP, ?, ?)',
			[query_key, total_found, new_added],
		)
