#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import random
import sys

from agentai.scraper import MediumScraper


async def run_batch(tags_str, date_context=None, limit=100):
	tags = tags_str.split()
	scraper = MediumScraper()

	print('\n🧩 BATCH PROCESSOR V2')
	print('-------------------------------------------')
	print(f'📅 Kontekst daty: {date_context if date_context else "BRAK (Tryb Search)"}')
	print(f'🏷️  Tagi do sprawdzenia: {", ".join(tags)}')
	print('-------------------------------------------')

	for tag in tags:
		# Budujemy zapytanie: jeśli jest data, to 'tag:data', jeśli nie, to sam 'tag'
		query = f'{tag}:{date_context}' if date_context else tag

		print(f'\n🚀 Skanuję: {tag.upper()}')
		try:
			await scraper.get_saved_stories(query, limit=limit)
		except Exception as e:
			print(f'❌ Błąd przy {tag}: {e}')

		# Bezpiecznik dla Medium
		wait = random.randint(7, 12)
		print(f'⏳ Przerwa techniczna: {wait}s...')
		await asyncio.sleep(wait)

	print('\n✅ Kolejka zakończona pomyślnie.')


if __name__ == '__main__':
	# Obsługa argumentów: <tags> <date> <limit>
	t_input = sys.argv[1] if len(sys.argv) > 1 else ''
	d_input = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '' else None
	l_input = sys.argv[3] if len(sys.argv) > 3 else 100

	asyncio.run(run_batch(t_input, d_input, l_input))
