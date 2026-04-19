#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
			# Inicjalizacja kontekstu z zachowaniem sesji (zalogowany użytkownik)
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
			except:
				pass

			# Jeśli nie podano URL, idziemy do widoku wszystkich list zalogowanego użytkownika
			target_url = query_or_url if query_or_url else 'https://medium.com/me/lists'

			# Rozpoznawanie trybu pracy
			is_all_lists_mode = '/me/lists' in target_url or target_url.endswith('/lists')

			if not is_all_lists_mode and not target_url.startswith('http'):
				if ':' in target_url:
					tag, date_str = target_url.split(':')
					formatted_date = date_str.replace('-', '/')
					target_url = f'https://medium.com/tag/{tag}/archive/{formatted_date}'
					mode = 'ARCHIVE'
				else:
					search_query = target_url.replace(' ', '%20')
					target_url = f'https://medium.com/search?q={search_query}'
					mode = 'SEARCH'
			elif is_all_lists_mode:
				mode = 'ALL_LISTS'
			elif '/list/' not in target_url and ('/p/' in target_url or '-' in target_url.split('/')[-1]):
				mode = 'SINGLE'
			else:
				mode = 'LIST'

			print('\n🚀 ROZPOCZĘTO SKANOWANIE')
			print(f'📊 Tryb: {mode} | Cel: {target_url}')
			print('---------------------------------------------------')

			await page.goto(target_url, wait_until='domcontentloaded')
			await asyncio.sleep(4)

			# Kolekcjonowanie list do skanowania w trybie HURTOWYM
			lists_to_scan = []
			if mode == 'ALL_LISTS':
				print('🔍 Szukam Twoich list na profilu...')
				lists_to_scan = await page.evaluate("""() => {
                const results = [];
                const anchors = document.querySelectorAll('a[href*="/list/"]');
                anchors.forEach(a => {
                    if (!results.includes(a.href)) results.push(a.href);
                });
                return results;
             }""")
				print(f'📂 Znaleziono list do sprawdzenia: {len(lists_to_scan)}')
			else:
				lists_to_scan = [target_url]

			total_added = 0
			total_seen = 0

			# Główna pętla przechodząca przez adresy URL
			for current_url in lists_to_scan:
				if mode == 'ALL_LISTS':
					print(f'\n📂 Wchodzę do listy: {current_url}')
					await page.goto(current_url, wait_until='domcontentloaded')
					await asyncio.sleep(3)

				if mode == 'SINGLE':
					title = (await page.title()).split('|')[0].strip()
					added = self.db.add_article(
						url=current_url.split('?')[0], title=title, topic='Manual', priority=10, source='manual_add'
					)
					print(f'✅ Dodano: {title}' if added else 'ℹ️ Już istnieje.')
					continue

				stuck_threshold = 0
				list_added = 0

				# Przewijanie i zbieranie linków
				while stuck_threshold < 15:
					# Obsługa przycisku "Show more"
					try:
						show_more = (
							page.get_by_role('button', name='Show more').or_by(page.get_by_text('Show more')).first
						)
						if await show_more.is_visible():
							print("🖱️ Klikam 'Show more'...")
							await show_more.click()
							await asyncio.sleep(2)
					except:
						pass

					# Ekstrakcja linków za pomocą JavaScript
					links = await page.evaluate("""() => {
                    const results = [];
                    const anchors = document.querySelectorAll('a[href*="/p/"], a[href*="---"]');
                    anchors.forEach(a => {
                        let title = a.innerText.trim();
                        if (title.length < 10) {
                            const p = a.closest('div, section, article');
                            const h = p ? p.querySelector('h2, h3') : null;
                            title = h ? h.innerText.trim() : title;
                        }
                        let finalUrl = a.href.split('?')[0];
                        if (title.length > 5 && !finalUrl.includes('/me/')) {
                            results.push({url: finalUrl, title: title.split('\\n')[0]});
                        }
                    });
                    return results;
                }""")

					added_in_loop = 0
					for item in links:
						# W trybie ALL_LISTS/LIST nie stosujemy limitu - czyścimy wszystko
						if mode not in ['ALL_LISTS', 'LIST'] and total_added >= int(limit):
							break

						added = self.db.add_article(
							url=item['url'],
							title=item['title'],
							topic='Research' if mode in ['SEARCH', 'ARCHIVE'] else 'Unsorted',
							priority=70 if mode in ['SEARCH', 'ARCHIVE'] else 50,
							source=f'medium_{mode.lower()}',
						)
						if added:
							total_added += 1
							list_added += 1
							added_in_loop += 1
							print(f'   [+] {total_added}: {item["title"][:60]}...')

					total_seen += len(links)

					# Logika przewijania i wykrywania końca treści
					if added_in_loop == 0:
						stuck_threshold += 1
						await page.keyboard.press('PageDown')
					else:
						stuck_threshold = 0
						print(f'   📥 Nowych w tej paczce: {added_in_loop} (Przejrzano: {len(links)})')

					await page.mouse.wheel(0, random.randint(800, 1200))
					await asyncio.sleep(1.5)

					# Wyjście z pętli jeśli osiągnięto limit w trybach wyszukiwania
					if mode in ['SEARCH', 'ARCHIVE'] and total_added >= int(limit):
						break

				print(f'✅ Zakończono skanowanie bieżącej lokalizacji. Dodano: {list_added}')

			# Raport końcowy
			duration = round(time.time() - start_time, 2)
			print('\n🏁 MISJA ZAKOŃCZONA')
			print(f'⏱️ Czas trwania: {duration}s')
			print(f'🔎 Przejrzano łącznie linków: {total_seen}')
			print(f'🆕 Dodano nowych artykułów: {total_added}')
			print(f'⏭️ Pominięto duplikatów: {total_seen - total_added}')
			print(f'📊 Efektywność skanowania: {round((total_added / total_seen) * 100, 1) if total_seen > 0 else 0}%')

			await context.close()


if __name__ == '__main__':
	# Przekazywanie argumentów z Makefile
	arg = sys.argv[1] if len(sys.argv) > 1 else None
	lim = sys.argv[2] if len(sys.argv) > 2 else 1000
	asyncio.run(MediumScraper().get_saved_stories(arg, lim))
