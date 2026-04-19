#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Moduł zarządcy procesów wsadowych (Batch Processor).

Umożliwia sekwencyjne skanowanie wielu tagów z kontrolą historii skanowania.
"""

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/lib/batch_processor.py
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
#       Zarządca procesów wsadowych. Pozwala na sekwencyjne uruchamianie scrapera dla
#       listy tagów, sprawdzając, czy nie powtarzać pracy dla tych samych fraz
#       w danym oknie czasowym.
#
#   CHANGELOG:
#       - 0.1: Inicjalizacja batch procesora.
#       - 0.2: Dodanie obsługi dat i kontekstów czasowych.
#       - 0.3 (19 IV 2026): Poprawa integracji z bazą i raportowania nowych rekordów.
# ==========================================================================================

import asyncio
import sys

from agentai.core.database import AgentDatabase
from agentai.core.scraper import MediumScraper

# Stałe
ARG_IDX_TAGS = 1
ARG_IDX_DATE = 2
ARG_IDX_LIMIT = 3
MIN_ARGS_LEN = 2
DEFAULT_LIMIT = 100


async def run_batch(tags_input: str, date_context: str | None = None, limit: int | str = 100):
	"""Uruchamia scraper dla serii tagów, sprawdzając, czy nie były skanowane.

	    :param tags_input: String z tagami oddzielonymi przecinkiem lub spacją.
	:param date_context: Kontekst czasowy skanowania (np. rok).
	:param limit: Maksymalna liczba artykułów na jeden tag.
	"""  # noqa: E101
	tags = [t.strip() for t in tags_input.split(',')] if ',' in tags_input else [t.strip() for t in tags_input.split()]

	scraper = MediumScraper()
	db = AgentDatabase()
	max_limit = int(limit)

	print('\n🧩 BATCH PROCESSOR V2.2')
	print('-------------------------------------------')
	print(f'📅 Kontekst: {date_context if date_context else "Bieżące"}')
	print(f'🏷️  Tagi: {", ".join(tags)}')

	for tag in tags:
		if not tag:
			continue

		query_key = f'{tag}:{date_context}' if date_context else tag

		if db.is_already_scanned(query_key):
			print(f'\n⏩ POMIJAM: {query_key} (już przeskanowano)')
			continue

		print(f'\n🚀 ROZPOCZYNAM SKAN: {tag.upper()}')

		try:
			# Sprawdzamy stan bazy przed skanem
			before = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]

			# 2. WYKONANIE SKANU
			await scraper.get_saved_stories(query_key, limit=max_limit)

			# Sprawdzamy stan bazy po skanie
			after = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]
			new_count = after - before

			# 3. AKTUALIZACJA HISTORII
			db.mark_as_scanned(query_key, total_found=max_limit, new_added=new_count)
			print(f'✅ ZAKOŃCZONO: {query_key} (Dodano: {new_count})')
		except Exception as e:
			print(f'❌ BŁĄD podczas skanowania {tag}: {e}')


if __name__ == '__main__':
	t_arg = sys.argv[ARG_IDX_TAGS] if len(sys.argv) > ARG_IDX_TAGS else ''
	d_arg = sys.argv[ARG_IDX_DATE] if len(sys.argv) > ARG_IDX_DATE else None
	l_arg = sys.argv[ARG_IDX_LIMIT] if len(sys.argv) > ARG_IDX_LIMIT else DEFAULT_LIMIT

	if len(sys.argv) < MIN_ARGS_LEN or not t_arg:
		print('❌ Błąd: Nie podano tagów do skanowania.')
		sys.exit(1)

	asyncio.run(run_batch(t_arg, d_arg, l_arg))
