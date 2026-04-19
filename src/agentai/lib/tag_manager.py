# =============================================================================
# AgentAI - Lib Tag Manager (PL <-> EN)
# =============================================================================
import os
import sys

from deep_translator import GoogleTranslator

# Definiujemy ścieżkę bezwzględną względem głównego folderu projektu
BASE_DIR = os.getcwd()
TAGS_FILE = os.path.join(BASE_DIR, 'data/tags.txt')


def load_tags():
	"""Wczytuje tagi, tylko jeśli plik istnieje i nie jest pusty."""
	if not os.path.exists(TAGS_FILE):
		return []
	try:
		with open(TAGS_FILE, encoding='utf-8') as f:
			lines = [l.strip() for l in f.readlines() if ':' in l]
			return lines
	except Exception as e:
		print(f'⚠️ Błąd podczas wczytywania pliku tagów: {e}')
		return []


def save_tags(tags):
	"""Zapisuje tagi z potrójnym zabezpieczeniem."""
	# BEZPIECZNIK 1: Nigdy nie nadpisuj pliku całkowitą pustką
	if not tags:
		print('⚠️ OSTRZEŻENIE: Próba zapisu pustej listy tagów. Operacja przerwana, by chronić bazę.')
		return

	os.makedirs(os.path.dirname(TAGS_FILE), exist_ok=True)

	# Sortowanie i usuwanie duplikatów przed zapisem
	unique_tags = sorted(list(set(tags)))

	try:
		with open(TAGS_FILE, 'w', encoding='utf-8') as f:
			for t in unique_tags:
				f.write(f'{t}\n')
		print(f'✅ Baza tagów zaktualizowana ({len(unique_tags)} pojęć).')
	except Exception as e:
		print(f'❌ Krytyczny błąd zapisu pliku: {e}')


def get_translation(text, target_lang='en'):
	source = 'pl' if target_lang == 'en' else 'en'
	try:
		return GoogleTranslator(source=source, target=target_lang).translate(text)
	except Exception as e:
		print(f'❌ Błąd tłumaczenia ({text}): {e}')
		return text


def process_add(input_str):
	current_tags = load_tags()
	# Zapamiętujemy początkową liczbę tagów, by wiedzieć, czy coś przybyło
	initial_count = len(current_tags)

	parts = [p.strip() for p in input_str.split(',')]

	global_en = parts[0].lower() == 'en'
	if global_en:
		parts = parts[1:]

	for part in parts:
		if not part:
			continue
		pl, en = None, None
		manual_pair = False  # Flaga trybu Express

		if '=' in part:
			pl, en = part.split('=')
			manual_pair = True
		elif ':' in part:
			pl, en = part.split(':')
			manual_pair = True
		elif global_en:
			en = part
			pl = get_translation(en, 'pl')
		else:
			pl = part
			en = get_translation(pl, 'en')

		# Jeśli to para ręczna (pl=en), dodaj od razu bez pytań
		if manual_pair:
			tag_entry = f'{pl.strip().lower()}:{en.strip().lower()}'
			current_tags.append(tag_entry)
			print(f'✅ Dodano (Express): {pl.strip()} <-> {en.strip()}')
		else:
			# Tryb interaktywny dla pojedynczych haseł
			print(f'\n🤖 PROPOZYCJA: PL({pl}) <-> EN({en})')
			choice = input('Zatwierdzić? [Y/n/edit]: ').lower()

			if choice == 'edit':
				pl = input(f'Nowy PL [{pl}]: ') or pl
				en = input(f'Nowy EN [{en}]: ') or en
				current_tags.append(f'{pl.strip().lower()}:{en.strip().lower()}')
			elif choice != 'n':
				current_tags.append(f'{pl.strip().lower()}:{en.strip().lower()}')

	# BEZPIECZNIK 2: Zapisuj tylko, jeśli faktycznie coś się zmieniło/dodało
	if len(current_tags) > initial_count:
		save_tags(current_tags)
	else:
		print('\nℹ️ Nie dodano nowych pojęć. Plik nienaruszony.')


def process_remove(input_str):
	current_tags = load_tags()
	if not current_tags:
		print('⚠️ Plik tagów jest pusty, nie ma czego usuwać.')
		return

	to_remove = [p.strip().lower() for p in input_str.split(',')]

	# Tworzymy nową listę bez elementów pasujących do wzorca
	new_tags = [line for line in current_tags if not any(r in line for r in to_remove)]

	if len(new_tags) < len(current_tags):
		# BEZPIECZNIK 3: Jeśli usuwanie miałoby wyczyścić wszystko, zapytaj o potwierdzenie
		if not new_tags:
			confirm = input('⚠️ Ta operacja USUNIE WSZYSTKIE TAGI. Czy na pewno? [y/N]: ').lower()
			if confirm != 'y':
				print('❌ Operacja anulowana.')
				return

		save_tags(new_tags)
		print(f'✅ Usunięto {len(current_tags) - len(new_tags)} tag(ów).')
	else:
		print('ℹ️ Nie znaleziono tagów pasujących do wzorca.')


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("Usage: python tag_manager.py [add|remove] 'content'")
		sys.exit(1)

	cmd, val = sys.argv[1], sys.argv[2]
	if cmd == 'add':
		process_add(val)
	elif cmd == 'remove':
		process_remove(val)
