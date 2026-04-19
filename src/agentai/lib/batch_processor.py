#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys

from agentai.core.database import AgentDatabase
from agentai.core.scraper import MediumScraper

# Stałe argumentów
ARG_IDX_TAGS = 1
ARG_IDX_DATE = 2
ARG_IDX_LIMIT = 3
MIN_ARGS_LEN = 2


async def run_batch(tags_input: str, date_context: str | None = None, limit: int | str = 100):
	"""Zarządca kolejki skanowania - wymusza skanowanie tag po tagu."""
	# Rozbijanie ciągu tagów (obsługuje przecinki i spacje)
	if ',' in tags_input:
		tags = [t.strip() for t in tags_input.split(',') if t.strip()]
	else:
		tags = [t.strip() for t in tags_input.split() if t.strip()]

	scraper = MediumScraper()
	db = AgentDatabase()
	max_limit = int(limit)

	print('\n🧩 BATCH PROCESSOR V2.2 [RE-SCAN MODE]')
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
			before = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]

			# WYWOŁANIE SCRAPERA (tutaj skrypt czeka na zakończenie roboty przez scraper.py)
			await scraper.get_saved_stories(query_key, limit=max_limit)

			# Pobieramy licznik bazy po skanie
			after = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]
			new_count = after - before

			# Oznaczamy w historii jako przeskanowane (aktualizujemy statystyki)
			db.mark_as_scanned(query_key, total_found=max_limit, new_added=new_count)

			print(f'\n✅ ZAKOŃCZONO TAG: {tag}')
			print(f'📊 Nowych rekordów: {new_count}')

			# Pauza między tagami dla bezpieczeństwa IP
			await asyncio.sleep(2)

		except Exception as e:
			print(f'❌ BŁĄD podczas procesowania {tag}: {e}')


if __name__ == '__main__':
	# Pobieranie argumentów z linii komend (przekazywanych przez Makefile)
	t_arg = sys.argv[ARG_IDX_TAGS] if len(sys.argv) > ARG_IDX_TAGS else ''
	d_arg = sys.argv[ARG_IDX_DATE] if len(sys.argv) > ARG_IDX_DATE else None
	l_arg = sys.argv[ARG_IDX_LIMIT] if len(sys.argv) > ARG_IDX_LIMIT else 100

	if not t_arg:
		print('❌ Błąd: Nie podano tagów do skanowania.')
		sys.exit(1)

	asyncio.run(run_batch(t_arg, d_arg, l_arg))
