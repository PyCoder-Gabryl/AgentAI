#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==========================================================================================
#   PROJEKT:            AgentAI
#   MODUŁ:              AgentAI/src/agentai/main.py
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
#       Główny punkt wejścia systemu AgentAI. Odpowiada za weryfikację integralności
#       bazy danych, sprawdzanie dostępności modeli AI oraz raportowanie
#       bieżącego stanu wiedzy agenta.
#
#   CHANGELOG:
#       - 0.1: Inicjalizacja punktu wejścia.
#       - 0.2 (19 kwi 2026): Dodanie szczegółowych statystyk statusów (pending/processed).
# ==========================================================================================

import sys

from agentai.core.database import AgentDatabase


def main():
	print('\n' + '=' * 50)
	print('🤖 AgentAI - SYSTEM STATUS CHECK')
	print('=' * 50)

	try:
		db = AgentDatabase()

		# Pobieranie statystyk z bazy
		total = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]
		pending = db.conn.execute("SELECT count(*) FROM articles WHERE status = 'pending'").fetchone()[0]
		processed = db.conn.execute("SELECT count(*) FROM articles WHERE status = 'processed'").fetchone()[0]
		rejected = db.conn.execute("SELECT count(*) FROM articles WHERE status = 'rejected'").fetchone()[0]

		print('📊 OGÓLNE STATYSTYKI:')
		print(f'   - Wszystkich rekordów: {total}')
		print(f'   - Oczekujące na AI:    {pending} (pending)')
		print(f'   - Przetworzone:        {processed} (processed)')
		print(f'   - Odrzucone/Śmieci:    {rejected} (rejected)')

		print('-' * 50)
		if pending > 0:
			print(f"💡 Sugestia: Masz {pending} artykułów do przetworzenia. Uruchom 'make agent-process'.")
		else:
			print('✅ Baza jest zaktualizowana. Brak nowych zadań dla AI.')
		print('🚀 System gotowy do pracy.\n')

	except Exception as e:
		print(f'❌ BŁĄD KRYTYCZNY INICJALIZACJI: {e}')
		sys.exit(1)


if __name__ == '__main__':
	main()
