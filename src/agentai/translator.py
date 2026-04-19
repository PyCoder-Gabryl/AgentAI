import csv
import os


class TagTranslator:
	def __init__(self, mapping_file='data/translations.csv'):
		self.mapping_file = mapping_file
		self.mapping = {}
		self.load_mapping()

	def load_mapping(self):
		if os.path.exists(self.mapping_file):
			with open(self.mapping_file, encoding='utf-8') as f:
				reader = csv.reader(f)
				self.mapping = {rows[0].strip().lower(): rows[1].strip().lower() for rows in reader if rows}

	def translate(self, tag):
		tag_clean = tag.strip().lower()

		# 1. Jeśli już jest w słowniku - zwróć wynik
		if tag_clean in self.mapping:
			return self.mapping[tag_clean]

		# 2. Jeśli tag nie ma polskich znaków, załóż że jest OK (angielski)
		pl_chars = 'ąćęłńóśźż'
		if not any(c in tag_clean for c in pl_chars):
			return tag_clean

		# 3. Jeśli jest polski, a nie ma go w słowniku - ostrzeż
		print(f"⚠️  Tag '{tag}' może wymagać tłumaczenia na angielski!")
		return tag_clean
