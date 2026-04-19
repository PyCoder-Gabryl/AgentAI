#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/core/scraper.py
#
#   WERSJA:             0.4 [04-19]
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
#       Silnik zbierający linki z Medium. Obsługuje tryby: LIST (pobieranie z list),
#       SEARCH (tagi) oraz ARCHIVE (filtrowanie po dacie). Wykorzystuje Playwright
#       z sesją użytkownika, aby omijać limity i logowania.
#
#   CHANGELOG:
#       - 0.1: Podstawowy scraper list.
#       - 0.2: Dodanie obsługi tagów i dat.
#       - 0.3: Integracja z DuckDB.
#       - 0.4 (19 kwi 2026): Optymalizacja pod procesor AI (status 'pending').
# ==========================================================================================

import asyncio
import os
import random
import sys
import time

from playwright.async_api import async_playwright

from agentai.core.database import AgentDatabase


class MediumScraper:
	def __init__(self, auth_path='auth.json'):
		self.auth_path = auth_path
		self.db = AgentDatabase()

	async def get_saved_stories(self, query_or_url=None, limit=1000):
		start_time = time.time()
		async with async_playwright() as p:
			# Używamy dedykowanego katalogu sesji dla scrapera
			user_data_dir = os.path.join(os.getcwd(), 'data/user_data_scraper')
			context = await p.chromium.launch_persistent_context(
				user_data_dir,
				headless=False,
				viewport={'width': 1280, 'height': 1000},
				args=['--disable-blink-features=AutomationControlled'],
			)
			page = context.pages[0] if context.pages else await context.new_page()

			try:
				from playwright_stealth import stealth

				await stealth(page)
			except ImportError:
				pass

			# Określenie celu i trybu
			if query_or_url and 'medium.com' in query_or_url:
				target_url = query_or_url
				mode = 'URL'
			elif query_or_url:
				# Jeśli podano tag (może być z datą: "python:2024")
				if ':' in query_or_url:
					tag, year = query_or_url.split(':')
					target_url = f'https://medium.com/search/posts?q={tag}%20year:{year}'
					mode = 'ARCHIVE'
				else:
					target_url = f'https://medium.com/tag/{query_or_url}'
					mode = 'SEARCH'
			else:
				target_url = 'https://medium.com/me/lists'
				mode = 'LIST'

			print(f'🕵️  Tryb: {mode} | Cel: {target_url}')
			await page.goto(target_url)
			await asyncio.sleep(2)

			total_added = 0
			total_seen = 0
			stuck_threshold = 0

			while total_added < int(limit) and stuck_threshold < 15:
				# Wyciągamy linki i tytuły (selektor dopasowany do Medium)
				articles = await page.query_selector_all('article, .postArticle')
				added_in_loop = 0

				for art in articles:
					try:
						title_elem = await art.query_selector('h2, h3, .graf--title')
						link_elem = await art.query_selector('a[href*="/p/"], a[data-post-id]')

						if title_elem and link_elem:
							title = await title_elem.inner_text()
							url = await link_elem.get_attribute('href')
							if url.startswith('/'):
								url = f'https://medium.com{url.split("?")[0]}'
							else:
								url = url.split('?')[0]

							# Próba dodania do bazy
							added = self.db.add_article(
								url=url,
								title=title.strip(),
								topic=query_or_url if query_or_url else 'Reading List',
								status='pending',
								source=f'medium_{mode.lower()}',
							)

							if added:
								total_added += 1
								added_in_loop += 1
								print(f'   [+] {total_added}: {title[:60]}...')
					except:
						continue

				total_seen += len(articles)

				# Przewijanie
				if added_in_loop == 0:
					stuck_threshold += 1
					await page.keyboard.press('PageDown')
				else:
					stuck_threshold = 0
					await page.mouse.wheel(0, random.randint(1000, 1500))

				await asyncio.sleep(random.uniform(1.0, 2.5))

			await context.close()

			duration = round(time.time() - start_time, 2)
			print(f'\n🏁 ZAKOŃCZONO: Dodano {total_added} (Przejrzano {total_seen}) w {duration}s')


if __name__ == '__main__':
	scraper = MediumScraper()
	arg = sys.argv[1] if len(sys.argv) > 1 else None
	lim = sys.argv[2] if len(sys.argv) > 2 else 1000
	asyncio.run(scraper.get_saved_stories(arg, lim))
