#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/core/database.py
#
#   WERSJA:             0.3 [04-19]
#   Data utworzenia:    2026 kwiecień 19, 21:15
#
#   COPYRIGHT:          2026 PyGamiQ <pygamiq@gmail.com>
#   LICENCJA:           MIT
#
#   AUTOR:              PyGamiQ
#   GITHUB:             https://github.com/PyGamiQ/agentai
#   IDE:                PyCharm Python 3.14.2 <macOS ARM>
# ==========================================================================================
#   OPIS:
#       Rdzeń systemu bazodanowego oparty na DuckDB. Zarządza tabelami artykułów,
#       historią skanowania oraz migracjami schematu (obsługa statusów i wersji PL).
#
#   CHANGELOG:
#       - 0.1 (19 kwi 2026): Inicjalizacja struktur bazy.
#       - 0.2 (19 kwi 2026): Dodanie kolumn title_pl i summary_pl.
#       - 0.3 (19 kwi 2026): Implementacja sanitize_database (obsługa statusu 'rejected').
# ==========================================================================================

import os

import duckdb


class AgentDatabase:
	def __init__(self, db_path='data/agent_knowledge.db'):
		os.makedirs(os.path.dirname(db_path), exist_ok=True)
		self.conn = duckdb.connect(db_path)
		self._setup_tables()
		self._migrate_tables()

	def _setup_tables(self):
		"""Inicjalizacja podstawowej struktury tabel."""
		self.conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                url VARCHAR PRIMARY KEY,
                title VARCHAR,
                topic VARCHAR,
                priority INTEGER,
                status VARCHAR DEFAULT 'pending',
                content_summary TEXT,
                title_pl VARCHAR,
                summary_pl TEXT,
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
		"""Dodaje nowe kolumny, jeśli jeszcze nie istnieją."""
		columns_info = self.conn.execute("PRAGMA table_info('articles')").fetchall()
		column_names = [col[1] for col in columns_info]

		if 'title_pl' not in column_names:
			self.conn.execute('ALTER TABLE articles ADD COLUMN title_pl VARCHAR')
		if 'summary_pl' not in column_names:
			self.conn.execute('ALTER TABLE articles ADD COLUMN summary_pl TEXT')
		if 'status' not in column_names:
			self.conn.execute("ALTER TABLE articles ADD COLUMN status VARCHAR DEFAULT 'pending'")

	def add_article(self, url, title, topic, status='pending', source='unknown'):
		"""Dodaje nowy artykuł, jeśli URL nie istnieje."""
		try:
			self.conn.execute(
				'INSERT OR IGNORE INTO articles (url, title, topic, status, source_account) VALUES (?, ?, ?, ?, ?)',
				[url, title, topic, status, source],
			)
			return self.conn.execute('SELECT changes()').fetchone()[0] > 0
		except Exception:
			return False

	def is_already_scanned(self, query_key):
		"""Sprawdza czy dany tag/url był już skanowany."""
		res = self.conn.execute('SELECT query_key FROM scan_history WHERE query_key = ?', [query_key]).fetchone()
		return res is not None

	def mark_as_scanned(self, query_key, total_found, new_added):
		"""Zapisuje fakt wykonania skanowania."""
		self.conn.execute(
			'INSERT OR REPLACE INTO scan_history (query_key, last_scanned, total_found, new_added) '
			'VALUES (?, CURRENT_TIMESTAMP, ?, ?)',
			[query_key, total_found, new_added],
		)

	def get_pending_articles(self, limit=10):
		"""Pobiera artykuły do przetworzenia przez AI."""
		return self.conn.execute(
			"SELECT url, title, topic FROM articles WHERE status = 'pending' LIMIT ?", [limit]
		).fetchall()

	def update_full_article(self, url, title_pl, summary_pl):
		"""Zapisuje wyniki pracy AI i zmienia status."""
		self.conn.execute(
			"UPDATE articles SET title_pl = ?, summary_pl = ?, status = 'processed' WHERE url = ?",
			[title_pl, summary_pl, url],
		)

	def sanitize_database(self):
		"""Oznacza śmieciowe linki jako 'rejected'."""
		trash_patterns = ['%/followers', '%/about', '%/lists', '%/subscribe', '%?source=%']
		count = 0
		for pattern in trash_patterns:
			self.conn.execute(
				"UPDATE articles SET status = 'rejected' WHERE url LIKE ? AND status != 'rejected'", [pattern]
			)

		self.conn.execute("UPDATE articles SET status = 'rejected' WHERE length(title) < 10 AND status != 'rejected'")
		return self.conn.execute("SELECT count() FROM articles WHERE status = 'rejected'").fetchone()[0]


if __name__ == '__main__':
	db = AgentDatabase()
	print('✅ Baza danych i tabele są gotowe.')
