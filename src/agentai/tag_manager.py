import os
import sys

from deep_translator import GoogleTranslator

TAGS_FILE = 'data/tags.txt'


def load_tags():
	if not os.path.exists(TAGS_FILE):
		return []
	with open(TAGS_FILE, encoding='utf-8') as f:
		return [l.strip() for l in f.readlines() if ':' in l]


def save_tags(tags):
	with open(TAGS_FILE, 'w', encoding='utf-8') as f:
		for t in sorted(list(set(tags))):
			f.write(f'{t}\n')


def get_translation(text, target_lang='en'):
	source = 'pl' if target_lang == 'en' else 'en'
	try:
		return GoogleTranslator(source=source, target=target_lang).translate(text)
	except:
		return text


def process_add(input_str):
	current_tags = load_tags()
	# Rozbijamy wejście po przecinkach
	parts = [p.strip() for p in input_str.split(',')]

	# Obsługa znacznika "en" na początku
	global_en = False
	if parts[0].lower() == 'en':
		global_en = True
		parts = parts[1:]

	for part in parts:
		if not part:
			continue
		pl, en = None, None

		# 1. Sprawdź format pl=en lub pl:en
		if '=' in part:
			pl, en = part.split('=')
		elif ':' in part:
			pl, en = part.split(':')
		# 2. Automatyczne wykrywanie / Tłumaczenie
		elif global_en:
			en = part
			pl = get_translation(en, 'pl')
		else:
			# Sprawdź czy ma polskie znaki
			pl = part
			en = get_translation(pl, 'en')

		# Interaktywne zatwierdzenie
		print(f'\nPROPOZYCJA: PL({pl}) <-> EN({en})')
		choice = input('Czy zatwierdzasz tę parę? [Y/n/edit]: ').lower()

		if choice == 'edit':
			pl = input(f'Podaj PL [{pl}]: ') or pl
			en = input(f'Podaj EN [{en}]: ') or en
			current_tags.append(f'{pl.strip().lower()}:{en.strip().lower()}')
		elif choice != 'n':
			current_tags.append(f'{pl.strip().lower()}:{en.strip().lower()}')

	save_tags(current_tags)


def process_remove(input_str):
	current_tags = load_tags()
	to_remove = [p.strip().lower() for p in input_str.split(',')]

	new_tags = []
	for line in current_tags:
		pl, en = line.split(':')
		# Usuń jeśli pasuje do PL, EN lub całej pary
		if pl in to_remove or en in to_remove or f'{pl}={en}' in to_remove:
			print(f'🔥 Usuwam: {line}')
			continue
		new_tags.append(line)

	save_tags(new_tags)


if __name__ == '__main__':
	cmd = sys.argv[1]
	val = sys.argv[2]
	if cmd == 'add':
		process_add(val)
	elif cmd == 'remove':
		process_remove(val)
