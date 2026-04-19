#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Moduł generatora sesji dla systemu AgentAI."""

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/lib/auth_generator.py
#
#   WERSJA:             1.0 [04-19]
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
#       Generator sesji uwierzytelniającej. Pozwala użytkownikowi na manualne zalogowanie
#       się do Medium i zapisanie sesji (ciasteczek), co omija zabezpieczenia Cloudflare.
#
#   CHANGELOG:
#       - 1.0 (19 IV 2026): Pełna stabilizacja, usunięcie zbędnych zależności i docstringi.
# ==========================================================================================

import asyncio
import os
import shutil

from playwright.async_api import ViewportSize, async_playwright


async def save_medium_session():
	"""Uruchamia przeglądarkę w trybie graficznym do manualnego zalogowania się.

	    Funkcja czyści stare dane sesji, otwiera nowe okno przeglądarki z emulacją
	użytkownika (User-Agent) i oczekuje, aż operator zamknie okno po zalogowaniu.
	"""  # noqa: E101
	user_data_dir = os.path.join(os.getcwd(), 'data/user_data_scraper')

	if os.path.exists(user_data_dir):
		print('🧹 Czyszczenie starej sesji...')
		try:
			shutil.rmtree(user_data_dir, ignore_errors=True)
		except OSError as e:
			print(f'⚠️ Błąd podczas usuwania katalogu sesji: {e}')

	async with async_playwright() as p:
		print('\n🚀 Uruchamiam instancję "Human-Like" pod kontrolą Agenta...')

		user_agent = (
			'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
			'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
		)

		my_viewport = ViewportSize(width=1280, height=900)

		context = await p.chromium.launch_persistent_context(
			user_data_dir,
			headless=False,
			user_agent=user_agent,
			args=['--disable-blink-features=AutomationControlled'],
			viewport=my_viewport,
		)

		page = context.pages[0] if context.pages else await context.new_page()

		print('👉 Otwieram stronę logowania Medium...')
		await page.goto('https://medium.com/m/signin')

		print('\n' + '!' * 30)
		print('INSTRUKCJA DLA OPERATORA:')
		print('1. Rozwiąż Cloudflare, jeśli się pojawi.')
		print('2. Zaloguj się na swoje konto Medium.')
		print('3. Gdy zobaczysz swój profil, zamknij okno przeglądarki.')
		print('!' * 30 + '\n')

		while True:
			try:
				if not context.pages:
					break
				await asyncio.sleep(1)
			except RuntimeError, Exception:
				break

		print('✅ Sesja została pomyślnie zapisana.')


if __name__ == '__main__':
	asyncio.run(save_medium_session())
