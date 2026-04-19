# =============================================================================
# AgentAI - Main Entry Point
# =============================================================================
from agentai.core.database import AgentDatabase


def main():
	print('🤖 AgentAI System Check')
	print('-----------------------')
	try:
		db = AgentDatabase()
		count = db.conn.execute('SELECT count(*) FROM articles').fetchone()[0]
		print(f'✅ Baza danych aktywna. Artykułów: {count}')
		print('🚀 System gotowy do pracy.')
	except Exception as e:
		print(f'❌ Błąd inicjalizacji: {e}')


if __name__ == '__main__':
	main()
