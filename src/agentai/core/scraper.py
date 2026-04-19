#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import random
import sys
import time

from playwright.async_api import async_playwright

from agentai.core.database import AgentDatabase

# ===========================================================
# KONFIGURACJA
# ===========================================================
STUCK_LIMIT = 50  # Ile razy przewijać bez znalezienia nowości przed poddaniem się
# ===========================================================


class MediumScraper:
	def __init__(self, auth_path='auth.json'):
		self.auth_path = auth_path
		self.db = AgentDatabase()

	async def get_saved_stories(self, query_or_url=None, limit=1000):
		start_time = time.time()
		async with async_playwright() as p:
			user_data_dir = os.path.join(os.getcwd(), 'data/user_data_scraper')
			context = await p.chromium.launch_persistent_context(
				user_data_dir,
				headless=False,
				viewport={'width': 1280, 'height': 1000},
				args=['--disable-blink-features=AutomationControlled'],
			)
			page = context.pages[0] if context.pages else await context.new_page()

			target_url = query_or_url if query_or_url else 'https://medium.com/me/lists'

			if not target_url.startswith('http'):
				if ':' in target_url:
					tag, date_str = target_url.split(':')
					target_url = f'https://medium.com/tag/{tag}/archive/{date_str.replace("-", "/")}'
					mode = 'ARCHIVE'
					topic_name = tag
				else:
					target_url = f'https://medium.com/search?q={target_url.replace(" ", "%20")}'
					mode = 'SEARCH'
					topic_name = query_or_url
			else:
				mode = 'DIRECT'
				topic_name = 'Web'

			print(f'\n🚀 SKANER URUCHOMIONY | Tryb: {mode} | Cel: {topic_name}')
			print(f'🔗 Link: {target_url}')
			print('---------------------------------------------------')

			await page.goto(target_url, wait_until='domcontentloaded')
			await asyncio.sleep(4)

			total_added = 0
			stuck_threshold = 0

			while total_added < int(limit) and stuck_threshold < STUCK_LIMIT:
				try:
					show_more = page.locator('button:has-text("Show more"), .load-more-button').first
					if await show_more.is_visible():
						await show_more.click()
						await asyncio.sleep(2)
				except:
					pass

				links = await page.evaluate("""() => {
					const results = [];
					const selectors = ['a[href*="/p/"]', 'a[href*="---"]', 'article a', 'h2 a', 'h3 a', 'div[role="article"] a'];
					const anchors = document.querySelectorAll(selectors.join(','));
					anchors.forEach(a => {
						const url = a.href.split('?')[0];
						if (url.includes('/me/') || url.includes('/tag/') || url.includes('/about')) return;
						let title = "";
						const parent = a.closest('article, section, div[role="article"]');
						if (parent) {
							const h = parent.querySelector('h1, h2, h3, h4');
							title = h ? h.innerText.trim() : a.innerText.trim();
						} else { title = a.innerText.trim(); }
						if (title.length > 5 && url.startsWith('http') && !results.some(r => r.url === url)) {
							results.push({url: url, title: title.split('\\n')[0]});
						}
					});
					return results;
				}""")

				added_in_loop = 0
				for item in links:
					if total_added >= int(limit):
						break

					count_before = self.db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]

					self.db.add_article(
						url=item['url'],
						title=item['title'],
						topic=topic_name,
						status='pending',
						source=f'medium_{mode.lower()}',
					)

					count_after = self.db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]

					if count_after > count_before:
						total_added += 1
						added_in_loop += 1
						print(f'   [+] {total_added}: {item["title"][:65]}...')

				if added_in_loop == 0:
					stuck_threshold += 1
					if len(links) > 0:
						print(f'   ⏳ Same duplikaty ({len(links)}). Szukam dalej... [{stuck_threshold}/{STUCK_LIMIT}]')
					await page.keyboard.press('PageDown')
				else:
					stuck_threshold = 0
					print(f'   📥 W tej paczce dodano: {added_in_loop}')

				await page.mouse.wheel(0, random.randint(800, 1500))
				await asyncio.sleep(random.uniform(1.5, 2.5))

			print(f'\n🏁 ZAKOŃCZONO: {topic_name} | Razem nowych: {total_added}')
			await context.close()


if __name__ == '__main__':
	arg = sys.argv[1] if len(sys.argv) > 1 else None
	lim = sys.argv[2] if len(sys.argv) > 2 else 1000
	asyncio.run(MediumScraper().get_saved_stories(arg, lim))
