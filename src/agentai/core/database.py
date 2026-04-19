# =============================================================================
# AgentAI - Core Database Module
# =============================================================================
import os

import duckdb


class AgentDatabase:
	def __init__(self, db_path='data/agent_knowledge.db'):
		# Upewnij się, że folder data istnieje
		os.makedirs(os.path.dirname(db_path), exist_ok=True)
		self.conn = duckdb.connect(db_path)
		self._setup_tables()

	def _setup_tables(self):
		"""Inicjalizacja struktury tabel."""
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

	def add_article(self, url, title, topic, priority, source='main'):
		try:
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
