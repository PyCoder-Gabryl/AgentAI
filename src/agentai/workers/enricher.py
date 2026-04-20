#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Procesor wzbogacający — Wersja Hybrydowa (Twoja Metoda 1 + Skuteczny Ratunek)."""

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/workers/enricher.py
#
#   WERSJA:             0.5 [04-21]
#   Data utworzenia:    2026 kwiecień 19, 21:15
#
#   COPYRIGHT:          2026 PyGamiQ <pygamiq@gmail.com>
#   LICENCJA:           MIT
#
#   AUTOR:              PyGamiQ
#   GITHUB:             https://github.com/PyGamiQ/agentai
# ==========================================================================================

import asyncio
import logging
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
				print(f'🚀 [{i}/{total}] Pobieram treść: {title[:50]}...')
				print(f'   🔗 Link: {url}')

				context = await browser.new_context(
					user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
				)
				page = await context.new_page()
				await page.set_extra_http_headers({'Referer': 'https://www.google.com/'})

				status = 'FAIL'
				content = ''
				char_count = 0

				# --- PRÓBA 1: TWÓJ KOD (Podstawowy, który pobiera 1, 3, 4, 5) ---
				try:
					await page.goto(url, wait_until='domcontentloaded', timeout=25000)
					try:
						await page.wait_for_selector('article p, .pw-post-body-paragraph', timeout=5000)
					except:
						pass

					for _ in range(3):
						await page.mouse.wheel(0, 800)
						await asyncio.sleep(0.5)

					content = await self._extract_content(page)
					char_count = len(content)

					if char_count < 600:  # Podniosłem próg, by nr 2 (325 zn.) na pewno wywołał ratunek
						raise ValueError('Mało treści')

				except Exception:
					# --- PRÓBA 2: TWÓJ KOD RATUNKOWY (Który radził sobie z nr 2) ---
					print('   ⚠️ Próba nr 1 nieudana (za mało treści lub timeout). Uruchamiam ratunek (Metoda 2)...')
					try:
						# Tutaj wstawiam Twój kod, który "przebija" blokadę na nr 2
						await page.goto(url, wait_until='domcontentloaded', timeout=20000)
						await asyncio.sleep(2)  # To jest kluczowy sleep z Twojego kodu

						for _ in range(3):
							await page.mouse.wheel(0, 800)
							await asyncio.sleep(0.5)

						content = await self._extract_content(page)
						char_count = len(content)
					except Exception as e2:
						print(f'   💥 Nawet ratunek zawiódł: {str(e2)[:40]}')

				# Weryfikacja i zapis (Twoja logika końcowa)
				if char_count > 600:
					status = 'SUKCES'
					print(f'   ✅ Sukces! Pobrano {char_count} znaków.')
				else:
					# Ostatnia szansa: Twoje 4s
					await asyncio.sleep(4)
					content = await self._extract_content(page)
					char_count = len(content)
					status = 'SUKCES' if char_count > 600 else 'BLOKADA'

					if status == 'SUKCES':
						print(f'   ✅ Sukces po opóźnieniu! ({char_count} zn.)')
					else:
						print(f'   ❌ Zbyt krótka treść ({char_count} zn.).')

				is_paywall = 'Member-only story' in content or char_count < 500
				self.db.update_article_content(url, content, status.lower(), is_paywall)
				summary_stats.append((title[:30], char_count, status))

				await context.close()

			await browser.close()

		# TWOJE PODSUMOWANIE
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
