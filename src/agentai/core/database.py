#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Moduł obsługi bazy danych DuckDB dla projektu AgentAI."""

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/core/database.py
#
#   WERSJA:             0.4 [04-20]
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
		self._migrate_schema()

	def _migrate_schema(self):
		"""Tworzy tabele lub dodaje brakujące kolumny (migracja)."""
		# 1. Główna tabela artykułów
		self.conn.execute("""
			CREATE TABLE IF NOT EXISTS articles (
				url STRING PRIMARY KEY,
				title STRING,
				title_pl STRING,
				summary_pl STRING,
				content_raw STRING,
				topic STRING,
				status STRING DEFAULT 'pending',
				source STRING,
				is_paywall BOOLEAN DEFAULT FALSE,
				iteration INTEGER DEFAULT 1,
				confidence_score FLOAT DEFAULT 0.0,
				model_name STRING,
				deleted_tags STRING,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		""")

		# 2. Historia skanowania
		self.conn.execute("""
			CREATE TABLE IF NOT EXISTS scan_history (
				query_key STRING PRIMARY KEY,
				last_scanned TIMESTAMP,
				total_found INTEGER,
				new_added INTEGER
			)
		""")

		# System migracji — dodawanie brakujących kolumn
		existing_cols = self.conn.execute("PRAGMA table_info('articles')").fetchall()
		col_names = [col[1] for col in existing_cols]

		updates = {
			'content_raw': 'STRING',
			'is_paywall': 'BOOLEAN DEFAULT FALSE',
			'iteration': 'INTEGER DEFAULT 1',
			'confidence_score': 'FLOAT DEFAULT 0.0',
			'model_name': 'STRING',
			'deleted_tags': 'STRING',
		}

		for col, dtype in updates.items():
			if col not in col_names:
				self.conn.execute(f'ALTER TABLE articles ADD COLUMN {col} {dtype}')

	def add_article(self, url, title, topic=None, status='pending', source=None):
		"""Dodaje nowy artykuł, ignorując duplikaty URL."""
		self.conn.execute(
			'INSERT OR IGNORE INTO articles (url, title, topic, status, source) VALUES (?, ?, ?, ?, ?)',
			[url, title, topic, status, source],
		)

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


if __name__ == '__main__':
	db = AgentDatabase()
	print('✅ Baza danych AgentAI jest gotowa.')
