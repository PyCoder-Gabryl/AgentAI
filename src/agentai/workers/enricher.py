#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Procesor wzbogacający — Wersja Dynamiczna (Pobiera tylko nowe)."""

import asyncio
import logging
from dataclasses import dataclass

import trafilatura
from playwright.async_api import async_playwright

# Zakładamy, że AgentDatabase jest w Twoim projekcie
from agentai.core.database import AgentDatabase


@dataclass
class EnricherConfig:
	model_name: str = 'llama3'
	# Zwiększamy domyślnie, ale sterujemy tym przy uruchamianiu
	batch_size: int = 3
	headless: bool = True


class ArticleEnricher:
	def __init__(self, config: EnricherConfig = EnricherConfig()):
		self.config = config
		self.db = AgentDatabase()
		self.logger = logging.getLogger('AgentAI.Enricher')

	async def _extract_content(self, page) -> str:
		"""Twoja sprawdzona logika ekstrakcji Markdown (Nienaruszona)."""
		html = await page.content()

		# 1. Trafilatura
		text_md = (
			trafilatura.extract(
				html, include_formatting=True, include_links=True, include_images=True, output_format='markdown'
			)
			or ''
		)

		# 2. Twój Fallback JS (Pancerny)
		if len(text_md) < 800:
			return await page.evaluate("""() => {
             const container = document.querySelector('article') || document.body;
             const elements = container.querySelectorAll('h1, h2, h3, p, pre, img');
             let result = [];

             for (let el of elements) {
                 let tag = el.tagName.toLowerCase();
                 let text = el.innerText ? el.innerText.trim() : '';

                 if (tag === 'h1' && text) result.push('# ' + text);
                 else if (tag === 'h2' && text) result.push('## ' + text);
                 else if (tag === 'h3' && text) result.push('### ' + text);
                 else if (tag === 'pre' && text) result.push('```\\n' + text + '\\n```');
                 else if (tag === 'img' && el.src) {
                     if (el.width > 100 || el.src.includes('miro.medium.com')) {
                         result.push('![grafika](' + el.src + ')');
                     }
                 }
                 else if (tag === 'p' && text.length > 25) {
                     let pText = text;
                     const links = el.querySelectorAll('a');
                     links.forEach(a => {
                         const linkText = a.innerText.trim();
                         if (linkText && pText.includes(linkText)) {
                              pText = pText.replace(linkText, `[${linkText}](${a.href})`);
                         }
                     });
                     result.push(pText);
                 }
             }
             return result.join('\\n\\n');
          }""")
		return text_md

	async def run_batch(self, limit: int = None):
		"""Pobiera artykuły, które mają status 'pending' LUB puste pole content."""
		# Jeśli podasz limit w wywołaniu, nadpisze ten z configu
		process_limit = limit or self.config.batch_size

		# KLUCZ: Ta metoda musi w SQL mieć: WHERE content IS NULL OR content = ''
		articles = self.db.get_pending_articles(limit=process_limit)

		if not articles:
			print('✨ Wszystkie artykuły są już przetworzone! Brak nowych zadań.')
			return

		total = len(articles)
		print(f'🏗️ Znaleziono {total} nowych artykułów do wzbogacenia.')
		summary_stats = []

		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=self.config.headless)

			for i, (url, title, topic) in enumerate(articles, 1):
				print(f'🚀 [{i}/{total}] Proces: {title[:50]}...')

				context = await browser.new_context(
					user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
				)
				page = await context.new_page()

				status = 'fail'
				content = ''
				char_count = 0

				try:
					await page.goto(url, wait_until='domcontentloaded', timeout=25000)
					# Krótki scroll dla lazy-loading
					for _ in range(2):
						await page.mouse.wheel(0, 1000)
						await asyncio.sleep(0.4)

					content = await self._extract_content(page)
					char_count = len(content)

					if char_count > 600:
						status = 'success'
						print(f'   ✅ Pobrano: {char_count} znaków.')
					else:
						status = 'short'
						print(f'   ⚠️ Treść zbyt krótka ({char_count} zn.).')

				except Exception as e:
					print(f'   ❌ Błąd: {str(e)[:50]}')
					status = 'error'

				# ZAPIS DO BAZY: To krytyczny moment.
				# Po tym wywołaniu artykuł nie powinien się już pojawiać w get_pending_articles.
				is_paywall = 'Member-only story' in content
				self.db.update_article_content(url, content, status, is_paywall)

				summary_stats.append((title[:30], char_count, status.upper()))
				await context.close()

			await browser.close()

		print('\n' + '=' * 55)
		print('📊 PODSUMOWANIE SESJI')
		print('-' * 55)
		for t, c, s in summary_stats:
			icon = '🟢' if s == 'SUCCESS' else '🔴'
			print(f'{icon} {s:8} | {c:6} zn. | {t}...')
		print('=' * 55)


if __name__ == '__main__':
	# Teraz możesz łatwo sterować ilością z poziomu kodu:
	enricher = ArticleEnricher()
	# Chcesz 20? Po prostu wpisz to tutaj:
	asyncio.run(enricher.run_batch(limit=10))
