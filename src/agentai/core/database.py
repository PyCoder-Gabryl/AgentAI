#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Moduł obsługi bazy danych DuckDB dla projektu AgentAI."""

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
# ==========================================================================================

import os

import duckdb


class AgentDatabase:
	"""Zarządza połączeniem i operacjami na bazie danych DuckDB."""

	def __init__(self, db_path='data/agent_knowledge.db'):
		"""Inicjalizuje bazę danych i przeprowadza migrację tabel."""
		os.makedirs(os.path.dirname(db_path), exist_ok=True)
		self.conn = duckdb.connect(db_path)
		self._setup_tables()
		self._migrate_tables()

	def _setup_tables(self):
		"""Inicjalizuje strukturę tabel artykułów i historii skanowania."""
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
		"""Dodaje brakujące kolumny do istniejącej tabeli artykułów."""
		columns_info = self.conn.execute("PRAGMA table_info('articles')").fetchall()
		column_names = [col[1] for col in columns_info]

		if 'title_pl' not in column_names:
			self.conn.execute('ALTER TABLE articles ADD COLUMN title_pl VARCHAR')
		if 'summary_pl' not in column_names:
			self.conn.execute('ALTER TABLE articles ADD COLUMN summary_pl TEXT')
		if 'status' not in column_names:
			self.conn.execute("ALTER TABLE articles ADD COLUMN status VARCHAR DEFAULT 'pending'")

	def add_article(self, url, title, topic, status='pending', source='unknown'):
		"""Dodaje artykuł do bazy, ignorując duplikaty URL."""
		try:
			self.conn.execute(
				'INSERT OR IGNORE INTO articles (url, title, topic, status, source_account) VALUES (?, ?, ?, ?, ?)',
				[url, title, topic, status, source],
			)
			res = self.conn.execute('SELECT changes()').fetchone()
			return res[0] > 0 if res else False
		except duckdb.Error:
			return False

	def is_already_scanned(self, query_key):
		"""Sprawdza, czy dany tag był już skanowany."""
		res = self.conn.execute('SELECT query_key FROM scan_history WHERE query_key = ?', [query_key]).fetchone()
		return res is not None

	def mark_as_scanned(self, query_key, total_found, new_added):
		"""Zapisuje wynik skanowania w historii."""
		self.conn.execute(
			'INSERT OR REPLACE INTO scan_history (query_key, last_scanned, total_found, new_added) '
			'VALUES (?, CURRENT_TIMESTAMP, ?, ?)',
			[query_key, total_found, new_added],
		)

	def get_pending_articles(self, limit=10):
		"""Pobiera listę artykułów oznaczonych jako pending."""
		return self.conn.execute(
			"SELECT url, title, topic FROM articles WHERE status = 'pending' LIMIT ?", [limit]
		).fetchall()

	def update_full_article(self, url, title_pl, summary_pl):
		"""Aktualizuje artykuł o tłumaczenie i zmienia status na processed."""
		self.conn.execute(
			"UPDATE articles SET title_pl = ?, summary_pl = ?, status = 'processed' WHERE url = ?",
			[title_pl, summary_pl, url],
		)

	def sanitize_database(self):
		"""Usuwa śmieciowe linki i krótkie tytuły z kolejki przetwarzania."""
		trash_patterns = ['%/followers', '%/about', '%/lists', '%/subscribe', '%?source=%']
		for pattern in trash_patterns:
			self.conn.execute(
				"UPDATE articles SET status = 'rejected' WHERE url LIKE ? AND status != 'rejected'", [pattern]
			)

		self.conn.execute("UPDATE articles SET status = 'rejected' WHERE length(title) < 10 AND status != 'rejected'")
		res = self.conn.execute("SELECT count() FROM articles WHERE status = 'rejected'").fetchone()
		return res[0] if res else 0


if __name__ == '__main__':
	db = AgentDatabase()
	db.sanitize_database()
	print('✅ Baza danych AgentAI gotowa do pracy.')
