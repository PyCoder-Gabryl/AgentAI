#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Procesor wzbogacający — Wersja Deep Scroll i lepsza diagnostyka."""

import asyncio
import logging
import random
from dataclasses import dataclass

import trafilatura
from playwright.async_api import async_playwright

from agentai.core.database import AgentDatabase


@dataclass
class EnricherConfig:
	model_name: str = 'llama3'
	batch_size: int = 5
	headless: bool = True


class ArticleEnricher:
	def __init__(self, config: EnricherConfig = EnricherConfig()):
		self.config = config
		self.db = AgentDatabase()
		self.logger = logging.getLogger('AgentAI.Enricher')

	async def _extract_content(self, page) -> str:
		"""Hybrydowa ekstrakcja treści (Trafilatura + Native)."""
		html = await page.content()
		text_traf = trafilatura.extract(html) or ''

		# Rozszerzone selektory o 'div[role="presentation"]' i 'section'
		text_native = await page.evaluate("""() => {
			const selectors = [
				'article p', 
				'.pw-post-body-paragraph', 
				'section p', 
				'div[role="presentation"] p',
				'p'
			];
			const nodes = document.querySelectorAll(selectors.join(', '));
			return Array.from(nodes)
				.map(n => n.innerText)
				.filter(t => t.length > 25)
				.join('\\n\\n');
		}""")

		return text_traf if len(text_traf) > len(text_native) else text_native

	async def run_batch(self):
		articles = self.db.get_pending_articles(limit=self.config.batch_size)
		if not articles:
			print('📭 Brak artykułów do przetworzenia.')
			return

		total = len(articles)
		summary_stats = []

		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=self.config.headless)

			for i, (url, title, topic) in enumerate(articles, 1):
				# ZMIANA: "Pobieram treść" zamiast "Procesuję"
				print(f'🚀 [{i}/{total}] Pobieram treść: {title[:50]}...')
				print(f'   🔗 Link: {url}')

				context = await browser.new_context(
					user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
				)
				page = await context.new_page()
				await page.set_extra_http_headers({'Referer': 'https://www.google.com/'})

				try:
					await page.goto(url, wait_until='domcontentloaded', timeout=25000)

					# NOWOŚĆ: Deep Scroll — przewijamy powoli w dół i w górę
					for _ in range(3):
						await page.mouse.wheel(0, 800)
						await asyncio.sleep(0.5)
					await asyncio.sleep(random.uniform(1, 2))

					content = await self._extract_content(page)
					char_count = len(content)

					if char_count > 600:
						print(f'   ✅ Sukces! Pobrano {char_count} znaków.')
						status = 'SUKCES'
					else:
						# Ostatnia szansa: czekamy jeszcze 3 sekundy, może JS doładuje treść
						await asyncio.sleep(3)
						content = await self._extract_content(page)
						char_count = len(content)
						status = 'SUKCES' if char_count > 600 else 'BLOKADA'

						if status == 'SUKCES':
							print(f'   ✅ Sukces po opóźnieniu! ({char_count} zn.)')
						else:
							print(f'   ❌ Zbyt krótka treść ({char_count} zn.).')

					summary_stats.append((title[:30], char_count, status))

				except Exception as e:
					print(f'   💥 Błąd: {str(e)[:50]}')
					summary_stats.append((title[:30], 0, 'BŁĄD'))

				await context.close()

			await browser.close()

		print('\n' + '=' * 55)
		print(f'📊 PODSUMOWANIE SESJI ({total} artykułów)')
		print('-' * 55)
		for t, c, s in summary_stats:
			icon = '🟢' if s == 'SUKCES' else '🔴'
			print(f'{icon} {s:8} | {c:6} zn. | {t}...')
		print('=' * 55)


if __name__ == '__main__':
	enricher = ArticleEnricher()
	asyncio.run(enricher.run_batch())
