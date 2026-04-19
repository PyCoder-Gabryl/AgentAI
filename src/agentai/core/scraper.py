#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Moduł scrapera dla platformy Medium.
Obsługuje zbieranie linków w trybach LIST, SEARCH oraz ARCHIVE.
"""  # noqa: D205

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
#       - 0.4 (19 IV 2026): Optymalizacja pod procesor AI (status 'pending').
# ==========================================================================================

import asyncio
import logging
import os
import secrets
import sys
import time

from playwright.async_api import ElementHandle, ViewportSize, async_playwright

try:
	from playwright_stealth import stealth as stealth_func
except ImportError:
	stealth_func = None

from agentai.core.database import AgentDatabase

# Stałe konfiguracyjne — eliminacja "magic values"
STUCK_THRESHOLD_LIMIT = 15
INITIAL_WAIT_TIME = 2
SCROLL_MIN = 1000
SCROLL_MAX = 1500
RANDOM_SLEEP_MIN = 1.0
RANDOM_SLEEP_MAX = 2.5
DURATION_PRECISION = 2


class MediumScraper:
	"""Silnik do automatycznego pobierania linków z platformy Medium."""

	def __init__(self, auth_path: str = 'auth.json'):
		"""Inicjalizuje scraper oraz połączenie z bazą danych.

		:param auth_path: Ścieżka do pliku sesji użytkownika.
		"""
		self.auth_path = auth_path
		self.db = AgentDatabase()
		logging.basicConfig(level=logging.INFO)
		self.logger = logging.getLogger(__name__)

	async def _parse_article(self, art: ElementHandle, query: str | None, mode: str) -> bool:
		"""Parsuje pojedynczy element artykułu i zapisuje go do bazy danych."""
		try:
			title_elem = await art.query_selector('h2, h3, .graf--title')
			link_elem = await art.query_selector('a[href*="/p/"], a[data-post-id]')

			if title_elem and link_elem:
				title_text = await title_elem.inner_text()
				raw_url = await link_elem.get_attribute('href')

				if not raw_url:
					return False

				url = f'https://medium.com{raw_url.split("?")[0]}' if raw_url.startswith('/') else raw_url.split('?')[0]

				return self.db.add_article(
					url=url,
					title=title_text.strip(),
					topic=query if query else 'Reading List',
					status='pending',
					source=f'medium_{mode.lower()}',
				)
		except Exception as e:
			self.logger.debug('Błąd podczas parsowania elementu artykułu: %s', e)
		return False

	@staticmethod
	def _determine_mode(query: str | None) -> tuple[str, str]:
		"""Analizuje wejście i zwraca odpowiedni URL oraz tryb działania."""
		if query and 'medium.com' in query:
			return query, 'URL'
		if query:
			if ':' in query:
				parts = query.split(':')
				tag, year = parts[0], parts[1]
				return f'https://medium.com/search/posts?q={tag}%20year:{year}', 'ARCHIVE'
			return f'https://medium.com/tag/{query}', 'SEARCH'
		return 'https://medium.com/me/lists', 'LIST'

	# noinspection PyCallingNonCallable
	async def get_saved_stories(self, query_or_url: str | None = None, limit: int | str = 1000):
		"""Uruchamia proces scrapowania dla zadanej frazy lub adresu URL."""
		start_time = time.time()
		max_limit = int(limit)

		async with async_playwright() as p:
			user_data_dir = os.path.join(os.getcwd(), 'data/user_data_scraper')
			v_size: ViewportSize = {'width': 1280, 'height': 1000}

			context = await p.chromium.launch_persistent_context(
				user_data_dir,
				headless=False,
				viewport=v_size,
				args=['--disable-blink-features=AutomationControlled'],
			)
			page = context.pages[0] if context.pages else await context.new_page()

			# Wyciszenie błędu "None object is not callable" przez jawną weryfikację
			if stealth_func and callable(stealth_func):
				await stealth_func(page)

			target_url, mode = self._determine_mode(query_or_url)

			print(f'🕵️  Tryb: {mode} | Cel: {target_url}')
			await page.goto(target_url)
			await asyncio.sleep(INITIAL_WAIT_TIME)

			total_added = 0
			total_seen = 0
			stuck_threshold = 0

			while total_added < max_limit and stuck_threshold < STUCK_THRESHOLD_LIMIT:
				articles = await page.query_selector_all('article, .postArticle')
				added_in_loop = 0

				for art in articles:
					# Rzutowanie na Any, aby uciszyć błąd "Class Coroutine does not define __await__"
					is_added = await self._parse_article(art, query_or_url, mode)  # type: ignore
					if is_added:
						total_added += 1
						added_in_loop += 1
						print(f'   [+] {total_added}: Artykuł dodany...')

					if total_added >= max_limit:
						break

				total_seen += len(articles)

				if added_in_loop == 0:
					stuck_threshold += 1
					await page.keyboard.press('PageDown')
				else:
					stuck_threshold = 0
					scroll_y = secrets.SystemRandom().randint(SCROLL_MIN, SCROLL_MAX)
					await page.mouse.wheel(0, scroll_y)

				sleep_t = secrets.SystemRandom().uniform(RANDOM_SLEEP_MIN, RANDOM_SLEEP_MAX)
				await asyncio.sleep(sleep_t)

			await context.close()
			duration = round(time.time() - start_time, DURATION_PRECISION)
			print(f'\n🏁 ZAKOŃCZONO: Dodano {total_added} (Przejrzano {total_seen}) w {duration}s')


if __name__ == '__main__':
	scraper_instance = MediumScraper()
	cmd_arg = sys.argv[1] if len(sys.argv) > 1 else None
	cmd_lim = sys.argv[2] if len(sys.argv) > 2 else 1000

	try:
		asyncio.run(scraper_instance.get_saved_stories(cmd_arg, cmd_lim))
	except KeyboardInterrupt:
		print('\nPrzerwano ręcznie.')
