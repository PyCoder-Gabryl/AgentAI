#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Moduł scrapera serwisu Medium dla systemu AgentAI."""

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/core/scraper.py
#
#   WERSJA:             1.6 [04-20]
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
#       Główny moduł skanujący. Wykorzystuje Playwright do ekstrakcji artykułów z Medium.
#       Obsługuje tryby wyszukiwania, archiwum oraz list użytkownika.
#
#   CHANGELOG:
#       - 1.6 (20 IV 2026): Ostateczne skrócenie linii poniżej 100 znaków.
# ==========================================================================================

import asyncio
import os
import secrets
import sys

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Locator, Page, ViewportSize, async_playwright

from agentai.core.database import AgentDatabase

# ===========================================================
# KONFIGURACJA
# ===========================================================
STUCK_LIMIT = 50
SCROLL_PAUSE = 2
LOOP_PAUSE = 2
WAIT_INITIAL = 4
MIN_TITLE_LEN = 5
TITLE_PREVIEW_LEN = 60
MIN_RANDOM_WHEEL = 800
MAX_RANDOM_WHEEL = 1500
MIN_RANDOM_SLEEP = 1.5
MAX_RANDOM_SLEEP = 2.5

# Stałe dla sys.argv
ARG_IDX_TARGET = 1
ARG_IDX_LIMIT = 2
# ===========================================================


class MediumScraper:
	"""Zarządza procesem ekstrakcji danych z serwisu Medium."""

	def __init__(self, auth_path: str = 'auth.json'):
		"""Inicjalizuje scrapera."""
		self.auth_path = auth_path
		self.db = AgentDatabase()

	async def get_saved_stories(self, query_or_url: str | None = None, limit: int | str = 1000) -> None:
		"""Pobiera artykuły z zadanej lokalizacji lub zapytania."""
		async with async_playwright() as p:
			user_data_dir = os.path.join(os.getcwd(), 'data/user_data_scraper')
			context = await p.chromium.launch_persistent_context(
				user_data_dir,
				headless=False,
				viewport=ViewportSize(width=1280, height=1000),
				args=['--disable-blink-features=AutomationControlled'],
			)
			page = context.pages[0] if context.pages else await context.new_page()
			target_url = query_or_url if query_or_url else 'https://medium.com/me/lists'

			mode, topic, final_url = self._resolve_target(target_url, query_or_url)

			print(f'\n🚀 SKANER | Tryb: {mode} | Cel: {topic}')
			print(f'🔗 Link: {final_url}')
			print('-' * 50)

			await page.goto(final_url, wait_until='domcontentloaded')
			await asyncio.sleep(WAIT_INITIAL)

			await self._main_loop(page, int(limit), mode, topic)
			await context.close()

	@staticmethod
	def _resolve_target(target_url: str, query_or_url: str | None) -> tuple[str, str | None, str]:
		"""Rozpoznaje tryb pracy na podstawie wejściowego URL lub zapytania."""
		if not target_url.startswith('http'):
			if ':' in target_url:
				tag, date_str = target_url.split(':')
				arch_url = f'https://medium.com/tag/{tag}/archive/{date_str.replace("-", "/")}'
				return 'ARCHIVE', tag, arch_url

			search_url = f'https://medium.com/search?q={target_url.replace(" ", "%20")}'
			return 'SEARCH', query_or_url, search_url

		return 'DIRECT', 'Web', target_url

	async def _main_loop(self, page: Page, limit: int, mode: str, topic: str | None) -> None:
		"""Główna pętla skanowania strony."""
		total_added = 0
		stuck_threshold = 0

		while total_added < limit and stuck_threshold < STUCK_LIMIT:
			try:
				btn_sel = 'button:has-text("Show more"), .load-more-button'
				show_more: Locator = page.locator(btn_sel).first
				if await show_more.is_visible():
					await show_more.click()
					await asyncio.sleep(SCROLL_PAUSE)
			except PlaywrightError:
				pass

			# Selektory rozbite na części, by nie przekraczać linii
			s_list = ['a[href*="/p/"]', 'a[href*="---"]', 'article a', 'h2 a', 'h3 a', 'div[role="article"] a']
			links = await page.evaluate(f"""() => {{
				const results = [];
				const anchors = document.querySelectorAll('{','.join(s_list)}');
				anchors.forEach(a => {{
					const url = a.href.split('?')[0];
					if (url.includes('/me/') || url.includes('/tag/') || url.includes('/about')) return;
					const parent = a.closest('article, section, div[role="article"]');
					const h = parent ? parent.querySelector('h1, h2, h3, h4') : null;
					const title = h ? h.innerText.trim() : a.innerText.trim();
					if (title.length > {MIN_TITLE_LEN} &&
						url.startsWith('http') &&
						!results.some(r => r.url === url)) {{
						results.push({{url: url, title: title.split('\\n')[0]}});
					}}
				}});
				return results;
			}}""")

			added_in_loop = await self._process_links(links, limit, total_added, mode, topic)
			total_added += added_in_loop

			if added_in_loop == 0:
				stuck_threshold += 1
				if len(links) > 0:
					print(f'   ⏳ Duplikaty ({len(links)}). [{stuck_threshold}/{STUCK_LIMIT}]')
				await page.keyboard.press('PageDown')
				await asyncio.sleep(LOOP_PAUSE)
			else:
				stuck_threshold = 0
				print(f'   📥 Dodano: {added_in_loop}')

			wheel_y = MIN_RANDOM_WHEEL + secrets.randbelow(MAX_RANDOM_WHEEL - MIN_RANDOM_WHEEL)
			await page.mouse.wheel(0, wheel_y)

			sleep_range = int((MAX_RANDOM_SLEEP - MIN_RANDOM_SLEEP) * 100)
			await asyncio.sleep(MIN_RANDOM_SLEEP + (secrets.randbelow(sleep_range) / 100.0))

		print(f'\n🏁 KONIEC: {topic} | Nowych: {total_added}')

	async def _process_links(self, links: list, limit: int, total_added: int, mode: str, topic: str | None) -> int:
		"""Przetwarza zebrane linki i dodaje je do bazy."""
		added_count = 0
		sql_count = 'SELECT count(*) FROM articles'
		for item in links:
			if (total_added + added_count) >= limit:
				break

			res_before = self.db.conn.execute(sql_count).fetchone()
			count_before = res_before[0] if res_before else 0

			self.db.add_article(
				url=item['url'], title=item['title'], topic=topic, status='pending', source=f'medium_{mode.lower()}'
			)

			res_after = self.db.conn.execute(sql_count).fetchone()
			count_after = res_after[0] if res_after else 0

			if count_after > count_before:
				added_count += 1
				print(f'   [+] {total_added + added_count}: {item["title"][:TITLE_PREVIEW_LEN]}...')

		return added_count


if __name__ == '__main__':
	t_arg = sys.argv[ARG_IDX_TARGET] if len(sys.argv) > ARG_IDX_TARGET else None
	l_arg = sys.argv[ARG_IDX_LIMIT] if len(sys.argv) > ARG_IDX_LIMIT else 1000
	asyncio.run(MediumScraper().get_saved_stories(t_arg, l_arg))
