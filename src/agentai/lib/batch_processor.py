#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Moduł procesora wsadowego do masowego skanowania tagów w serwisie Medium."""

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/lib/batch_processor.py
#
#   WERSJA:             2.3 [04-20]
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
#       Zarządza kolejką zadań dla scrapera. Pozwala na sekwencyjne przetwarzanie
#       wielu tagów z opcjonalnym kontekstem daty, aktualizując statystyki bazy.
# ==========================================================================================

import asyncio
import sys

from agentai.core.database import AgentDatabase
from agentai.core.scraper import MediumScraper

# Stałe argumentów
ARG_IDX_TAGS = 1
ARG_IDX_DATE = 2
ARG_IDX_LIMIT = 3


async def run_batch(tags_input: str, date_context: str | None = None, limit: int | str = 100):
	"""Zarządca kolejki skanowania — wymusza skanowanie tag po tagu.

	Args:
		tags_input (str): Lista tagów oddzielona przecinkami lub spacjami.
		date_context (str | None): Opcjonalny rok/miesiąc dla archiwum Medium.
		limit (int | str): Maksymalna liczba artykułów do pobrania na jeden tag.
	"""
	# Rozbijanie ciągu tagów (obsługuje przecinki i spacje)
	if ',' in tags_input:
		tags = [t.strip() for t in tags_input.split(',') if t.strip()]
	else:
		tags = [t.strip() for t in tags_input.split() if t.strip()]

	scraper = MediumScraper()
	db = AgentDatabase()
	max_limit = int(limit)

	print('\n🧩 BATCH PROCESSOR V2.3 [RE-SCAN MODE]')
	print('-------------------------------------------')
	print(f'📅 Kontekst: {date_context if date_context else "Bieżące"}')
	print(f'🏷️  Liczba tagów w kolejce: {len(tags)}')

	for tag in tags:
		if not tag:
			continue

		# Budujemy klucz (np. python:2012)
		query_key = f'{tag}:{date_context}' if date_context else tag

		print(f'\n🔥 >>> ROZPOCZYNAM SEKWENCJĘ DLA: {tag.upper()} <<<')

		try:
			# Pobieramy licznik bazy przed skanem
			sql_count = 'SELECT count(*) FROM articles'
			before = db.conn.execute(sql_count).fetchone()[0]

			# WYWOŁANIE SCRAPERA
			await scraper.get_saved_stories(query_key, limit=max_limit)

			# Pobieramy licznik bazy po skanie
			after = db.conn.execute(sql_count).fetchone()[0]
			new_count = after - before

			# Oznaczamy w historii jako przeskanowane
			db.mark_as_scanned(query_key, total_found=max_limit, new_added=new_count)

			print(f'\n✅ ZAKOŃCZONO TAG: {tag}')
			print(f'📊 Nowych rekordów: {new_count}')

			# Pauza między tagami dla bezpieczeństwa IP
			await asyncio.sleep(2)

		except Exception as e:
			print(f'❌ BŁAD podczas procesowania {tag}: {e}')


if __name__ == '__main__':
	# Pobieranie argumentów z linii komend (przekazywanych przez Makefile)
	t_arg = sys.argv[ARG_IDX_TAGS] if len(sys.argv) > ARG_IDX_TAGS else ''
	d_arg = sys.argv[ARG_IDX_DATE] if len(sys.argv) > ARG_IDX_DATE else None
	l_arg = sys.argv[ARG_IDX_LIMIT] if len(sys.argv) > ARG_IDX_LIMIT else 100

	if not t_arg:
		print('❌ Błąd: Nie podano tagów do skanowania.')
		sys.exit(1)

	asyncio.run(run_batch(t_arg, d_arg, l_arg))
