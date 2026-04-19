#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Moduł zarządzania tagami i tłumaczeniami pojęć."""

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/lib/tag_manager.py
#
#   WERSJA:             0.4 [04-19]
# ==========================================================================================

import os
import sys

try:
	from deep_translator import GoogleTranslator
except ImportError:
	GoogleTranslator = None

# Stałe projektu
BASE_DIR = os.getcwd()
TAGS_FILE = os.path.join(BASE_DIR, 'data/tags.txt')
MIN_ARGS_COUNT = 2


def load_tags():
	"""Wczytuje pary pojęć z pliku tekstowego."""
	if not os.path.exists(TAGS_FILE):
		return []
	try:
		with open(TAGS_FILE, encoding='utf-8') as f:
			return [line.strip() for line in f.readlines() if ':' in line]
	except OSError as e:
		print(f'⚠️ Błąd odczytu bazy pojęć: {e}')
		return []


def save_tags(tags):
	"""Zapisuje tagi do pliku z automatycznym sortowaniem."""
	if not tags:
		print('⚠️ Próba zapisu pustej bazy pojęć zablokowana!')
		return

	os.makedirs(os.path.dirname(TAGS_FILE), exist_ok=True)
	unique_tags = sorted(set(tags))

	try:
		with open(TAGS_FILE, 'w', encoding='utf-8') as f:
			f.write('\n'.join(unique_tags) + '\n')
		print(f'✅ Baza pojęć zaktualizowana ({len(unique_tags)} wpisów).')
	except OSError as e:
		print(f'❌ Błąd zapisu bazy pojęć: {e}')


def get_translation(text, target_lang='en'):
	"""Tłumaczy tekst korzystając z bazy lokalnej lub Google Translatora."""
	tags = load_tags()
	mapping = {}

	for line in tags:
		if ':' in line:
			pl_term, en_term = line.split(':', 1)
			mapping[pl_term.strip().lower()] = en_term.strip().lower()
			mapping[en_term.strip().lower()] = pl_term.strip().lower()

	clean_text = text.strip().lower()

	if clean_text in mapping:
		return mapping[clean_text]

	if GoogleTranslator is None:
		return text

	try:
		source_lang = 'pl' if target_lang == 'en' else 'en'
		return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
	except RuntimeError, Exception:
		return text


def process_add(input_str):
	"""Interaktywne dodawanie nowych pojęć."""
	current_tags = load_tags()
	new_pairs = input_str.split(',')

	for pair in new_pairs:
		if '=' in pair:
			pl_part, en_part = pair.split('=')
			entry = f'{pl_part.strip().lower()}:{en_part.strip().lower()}'
			if entry not in current_tags:
				current_tags.append(entry)
				print(f'➕ Dodano: {pl_part} -> {en_part}')

	save_tags(current_tags)


def process_remove(input_str):
	"""Usuwanie pojęć z bazy."""
	current_tags = load_tags()
	to_remove = [r.strip().lower() for r in input_str.split(',')]

	new_tags = [t for t in current_tags if not any(r in t for r in to_remove)]

	if len(new_tags) < len(current_tags):
		save_tags(new_tags)
		print(f'🗑️ Usunięto {len(current_tags) - len(new_tags)} pojęć.')
	else:
		print('ℹ️ Nie znaleziono pasujących pojęć do usunięcia.')


if __name__ == '__main__':
	if len(sys.argv) < MIN_ARGS_COUNT:
		print('Użycie: tag_manager.py [add|remove] "fraza1=fraza2"')
		sys.exit(1)

	cmd = sys.argv[1].lower()
	val = sys.argv[2] if len(sys.argv) > MIN_ARGS_COUNT else ''

	if cmd == 'add':
		process_add(val)
	elif cmd == 'remove':
		process_remove(val)
	elif cmd == 'sort':
		save_tags(load_tags())
