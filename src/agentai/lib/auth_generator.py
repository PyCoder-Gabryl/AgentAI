#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/lib/auth_generator.py
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
#       Generator sesji uwierzytelniającej. Uruchamia instancję przeglądarki w trybie
#       graficznym (headed), pozwalając użytkownikowi na manualne zalogowanie się
#       do Medium i rozwiązanie zabezpieczeń Cloudflare. Sesja jest zapisywana
#       lokalnie i współdzielona ze scraperem.
#
#   CHANGELOG:
#       - 0.1: Podstawowa obsługa sesji Playwright.
#       - 0.2: Dodanie nagłówków Human-Like.
#       - 0.3 (19 kwi 2026): Optymalizacja czyszczenia starych danych sesji.
# ==========================================================================================

import asyncio
import os
import shutil

from playwright.async_api import async_playwright


async def save_medium_session():
	"""Uruchamia przeglądarkę do manualnego logowania."""
	user_data_dir = os.path.join(os.getcwd(), 'data/user_data_scraper')

	# Czyszczenie poprzedniej sesji, jeśli istnieje
	if os.path.exists(user_data_dir):
		print('🧹 Czyszczenie starej sesji...')
		try:
			shutil.rmtree(user_data_dir, ignore_errors=True)
		except Exception as e:
			print(f'⚠️ Uwaga przy sprzątaniu: {e}')

	async with async_playwright() as p:
		print('\n🚀 Uruchamiam instancję "Human-Like" pod kontrolą Agenta...')

		# Tworzymy kontekst z unikalnym User Agentem i wyłączonymi flagami automatyzacji
		context = await p.chromium.launch_persistent_context(
			user_data_dir,
			headless=False,
			user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
			args=['--disable-blink-features=AutomationControlled'],
			viewport={'width': 1280, 'height': 900},
		)

		page = context.pages[0] if context.pages else await context.new_page()

		# Próba wstrzyknięcia stealth (jeśli biblioteka jest dostępna)
		try:
			from playwright_stealth import stealth

			await stealth(page)
		except ImportError:
			pass

		print('👉 Otwieram stronę logowania Medium...')
		await page.goto('https://medium.com/m/signin')

		print('\n' + '!' * 30)
		print('INSTRUKCJA DLA OPERATORA:')
		print('1. Rozwiąż Cloudflare, jeśli się pojawi.')
		print('2. Zaloguj się na swoje konto Medium.')
		print('3. Gdy zobaczysz swój profil (stronę główną), zamknij okno przeglądarki.')
		print('!' * 30 + '\n')

		# Czekamy na zamknięcie przeglądarki przez użytkownika
		while True:
			try:
				if not context.pages:
					break
				await asyncio.sleep(1)
			except Exception:
				break

		print('✅ Sesja została zapisana w data/user_data_scraper.')


if __name__ == '__main__':
	asyncio.run(save_medium_session())
