#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
#       listy tagów, sprawdzając historię skanowania, aby nie powtarzać pracy
#       dla tych samych fraz w danym oknie czasowym.
#
#   CHANGELOG:
#       - 0.1: Inicjalizacja batch procesora.
#       - 0.2: Dodanie obsługi dat i kontekstów czasowych.
#       - 0.3 (19 kwi 2026): Poprawa integracji z bazą i raportowania nowych rekordów.
# ==========================================================================================

import asyncio
import sys

from agentai.core.database import AgentDatabase
from agentai.core.scraper import MediumScraper


async def run_batch(tags_input, date_context=None, limit=100):
	"""Uruchamia scraper dla serii tagów."""
	# Parsowanie wejścia (przecinki lub spacje)
	if ',' in tags_input:
		tags = [t.strip() for t in tags_input.split(',')]
	else:
		tags = [t.strip() for t in tags_input.split()]

	scraper = MediumScraper()
	db = AgentDatabase()

	print('\n🧩 BATCH PROCESSOR V2.2')
	print('-------------------------------------------')
	print(f'📅 Kontekst: {date_context if date_context else "Bieżące"}')
	print(f'🏷️  Tagi: {", ".join(tags)}')

	for tag in tags:
		if not tag:
			continue

		# Tworzenie klucza zapytania (np. "python:2024" lub po prostu "python")
		query_key = f'{tag}:{date_context}' if date_context else tag

		# 1. SPRAWDZENIE HISTORII
		if db.is_already_scanned(query_key):
			print(f'\n⏩ POMIJAM: {query_key} (już przeskanowano)')
			continue

		print(f'\n🚀 ROZPOCZYNAM SKAN: {tag.upper()}')

		try:
			# Sprawdzamy stan bazy przed skanem
			before = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]

			# 2. WYKONANIE SKANU
			await scraper.get_saved_stories(query_key, limit=int(limit))

			# Sprawdzamy stan bazy po skanie
			after = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]
			new_count = after - before

			# 3. AKTUALIZACJA HISTORII
			db.mark_as_scanned(query_key, total_found=limit, new_added=new_count)
			print(f'✅ ZAKOŃCZONO: {query_key} (Dodano: {new_count})')

		except Exception as e:
			print(f'❌ BŁĄD podczas skanowania {tag}: {e}')


if __name__ == '__main__':
	tags_arg = sys.argv[1] if len(sys.argv) > 1 else ''
	date_arg = sys.argv[2] if len(sys.argv) > 2 else None
	limit_arg = sys.argv[3] if len(sys.argv) > 3 else 100

	if not tags_arg:
		print('❌ Błąd: Nie podano tagów do skanowania.')
		sys.exit(1)

	asyncio.run(run_batch(tags_arg, date_arg, limit_arg))
