#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/lib/processor.py
#
#   WERSJA:             0.2 [04-19]
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
#       Procesor AI wzbogacający rekordy. Wchodzi w każdy URL, pobiera pełną treść artykułu
#       za pomocą Playwright, a następnie generuje techniczne streszczenie przez Ollama.
#
#   CHANGELOG:
#       - 0.1 (19 kwi 2026): Inicjalizacja modułu.
#       - 0.2 (19 kwi 2026): Dodanie asynchronicznego pobierania treści (Playwright).
# ==========================================================================================

import asyncio

import requests
from playwright.async_api import async_playwright

from agentai.core.database import AgentDatabase
from agentai.lib.tag_manager import get_translation


class AIProcessor:
	def __init__(self):
		self.db = AgentDatabase()
		self.model = 'llama3'

	async def fetch_article_content(self, page, url):
		"""Wchodzi w URL i wyciąga czysty tekst artykułu (mięso)."""
		try:
			# wait_until="networkidle" jest pewniejsze dla Medium, by załadować treść
			await page.goto(url, wait_until='domcontentloaded', timeout=30000)

			# Wyciągamy tekst z paragrafów wewnątrz tagu article
			content = await page.eval_on_selector_all('article p', "nodes => nodes.map(n => n.innerText).join('\n')")
			return content[:5000] if content else ''
		except Exception as e:
			print(f'⚠️ Nie udało się pobrać treści z {url}: {e}')
			return ''

	def generate_summary(self, title, topic, full_text):
		"""Generuje punktowe streszczenie na podstawie PEŁNEJ treści."""
		source_material = full_text if len(full_text) > 200 else title

		prompt = f"""
        Jesteś ekspertem IT. Na podstawie poniższego tekstu artykułu o temacie "{topic}":

        "{source_material}"

        Stwórz konkretne, techniczne streszczenie w języku polskim w formie 3-5 punktów.
        Skup się na kluczowych wnioskach, narzędziach i rozwiązaniach.
        Nie dodawaj wstępów typu "Artykuł omawia...".
        """
		try:
			response = requests.post(
				'http://localhost:11434/api/generate',
				json={'model': self.model, 'prompt': prompt, 'stream': False},
				timeout=60,
			)
			return response.json().get('response', '').strip()
		except Exception as e:
			return f'⚠️ Błąd AI: {e}'

	async def run(self, limit=5):
		"""Główna pętla procesora."""
		pending = self.db.get_pending_articles(limit)
		if not pending:
			print('📭 Brak artykułów do przetworzenia.')
			return

		print(f'🧠 Rozpoczynam głęboką analizę {len(pending)} artykułów...')

		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=True)
			page = await browser.new_page()

			for url, title, topic in pending:
				print(f'\n🚀 Analizuję: {title[:60]}...')

				# 1. Pobieranie treści
				full_text = await self.fetch_article_content(page, url)

				# 2. Tłumaczenie tytułu
				title_pl = get_translation(title, 'pl')

				# 3. Generowanie streszczenia (na podstawie treści lub tytułu jako fallback)
				summary_pl = self.generate_summary(title, topic, full_text)

				# 4. Zapis do bazy
				self.db.update_full_article(url, title_pl, summary_pl)
				print('✅ Przetworzono i zapisano.')

			await browser.close()


if __name__ == '__main__':
	proc = AIProcessor()
	asyncio.run(proc.run(limit=5))
