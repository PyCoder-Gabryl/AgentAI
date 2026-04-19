#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import shutil

from playwright.async_api import async_playwright

# Importujemy funkcję stealth bezpośrednio z pakietu
from playwright_stealth import stealth


async def save_medium_session():
	async with async_playwright() as p:
		user_data_dir = os.path.join(os.getcwd(), 'data/user_data')

		if os.path.exists(user_data_dir):
			try:
				shutil.rmtree(user_data_dir, ignore_errors=True)
			except Exception as e:
				print(f'⚠️ Uwaga przy czyszczeniu: {e}')

		print('\n🚀 Uruchamiam instancję "Human-Like" pod kontrolą Agenta...')

		# Persistent context to klucz do Cloudflare
		context = await p.chromium.launch_persistent_context(
			user_data_dir,
			headless=False,
			user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
			args=[
				'--disable-blink-features=AutomationControlled',
			],
		)

		page = context.pages[0] if context.pages else await context.new_page()

		# WYWOŁANIE ASYNCHRONICZNE (jeśli stealth z biblioteki tego wymaga)
		# W większości wersji playwright-stealth, stealth(page) jest synchroniczne
		# i modyfikuje prototypy strony.
		try:
			# Próbujemy standardowego wywołania
			stealth(page)
		except Exception as e:
			print(f'ℹ️ Info o Stealth: {e}')

		print('👉 Otwieram Medium...')
		await page.goto('https://medium.com/m/signin')

		print('\n--- INSTRUKCJA DLA CIEBIE ---')
		print('1. Rozwiąż Cloudflare (jeśli trzeba).')
		print('2. Zaloguj się na Medium.')
		print('3. ZAMKNIJ OKNO PRZEGLĄDARKI, gdy zobaczysz swój profil.')
		print('-----------------------------\n')

		while True:
			try:
				await asyncio.sleep(1)
				if page.is_closed():
					break
			except:
				break

		print('💾 Przechwytywanie sesji...')
		await context.storage_state(path='auth.json')
		print('\n✅ Gotowe! Plik auth.json został pomyślnie wygenerowany.')

		await context.close()


if __name__ == '__main__':
	os.makedirs('data', exist_ok=True)
	asyncio.run(save_medium_session())
