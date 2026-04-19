#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import random
import sys

from agentai.database import AgentDatabase
from agentai.scraper import MediumScraper


async def run_batch(tags_input, date_context=None, limit=100):
	# Rozdzielamy po przecinku, jeśli jest, w przeciwnym razie po spacji
	if ',' in tags_input:
		tags = [t.strip() for t in tags_input.split(',')]
	else:
		tags = [t.strip() for t in tags_input.split()]

	scraper = MediumScraper()
	db = AgentDatabase()

	print('\n🧩 BATCH PROCESSOR V2.1')
	print('-------------------------------------------')
	print(f'📅 Kontekst: {date_context if date_context else "Bieżące"}')
	print(f'🏷️  Tagi: {", ".join(tags)}')

	for tag in tags:
		if not tag:
			continue
		query_key = f'{tag}:{date_context}' if date_context else tag

		# 1. SPRAWDZENIE PAMIĘCI
		if db.is_already_scanned(query_key):
			print(f'\n⏩ POMIJAM: {query_key} (już jest w historii)')
			continue

		print(f'\n🚀 SKANUJĘ: {tag.upper()}')

		try:
			# 2. WYKONANIE SKANU
			# Tu scraper wykonuje robotę i dodaje do 'articles'
			# (get_saved_stories nie zwraca liczby, więc musimy to sprawdzić w bazie)
			before = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]

			await scraper.get_saved_stories(query_key, limit=int(limit))

			after = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]
			new_count = after - before

			# 3. ZAPISANIE DO HISTORII
			db.mark_as_scanned(query_key, total_found=limit, new_added=new_count)
			print(f'✅ ZAKOŃCZONO: {query_key} (Dodano: {new_count} nowych)')

		except Exception as e:
			print(f'❌ BŁĄD przy {tag}: {e}')

		# Bezpiecznik
		wait = random.randint(8, 15)
		print(f'⏳ Oddech: {wait}s...')
		await asyncio.sleep(wait)


if __name__ == '__main__':
	t_in = sys.argv[1] if len(sys.argv) > 1 else ''
	d_in = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '' else None
	l_in = sys.argv[3] if len(sys.argv) > 3 else 100
	asyncio.run(run_batch(t_in, d_in, l_in))
