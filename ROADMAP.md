# 🗺️ Roadmap: Knowledge Weaver (AgentAI)

## ✅ Faza 0: Fundamenty (ZAKOŃCZONE)

- [x] **Środowisko**: Konfiguracja Python 3.14 + venv + Makefile.
- [x] **Baza Danych**: Inicjalizacja DuckDB (`articles`) z systemem czyszczenia śmieci.
- [x] **Scraper V2**: Obsługa ARCHIVE, SEARCH, LIST. Automatyczne scrollowanie i sesje Playwright.
- [x] **Express Tag Manager**: System parowania pojęć PL <-> EN z trybem błyskawicznym (`tag=tag`) i autotłumaczeniem.
- [x] **Safety First**: System automatycznych backupów bazy tagów i walidacji przed zapisem.

---

## ⚙️ Faza 1: Autonomia i Zarządzanie Stanem (W TRAKCIE)

*Cel: Sprawić, by Agent pracował bez nadzoru i wiedział, co już zrobił.*

- [x] **Multi-Tag Loop**: Automatyczne skanowanie całej bazy pojęć (`make agent-scan-core`).
- [x] **Archive Catch-up**: Możliwość nadrabiania historii od 2012 roku dla wybranych dat (`make agent-scan-date`).
- [x] **Smart History**: Agent automatycznie pomija linki, które już posiada w DuckDB (ochrona przed duplikatami).
- [ ] **AgentAI.md (Master Control)**: Stworzenie pliku zasad w Obsidianie (protokół antyhalucynacyjny).
- [ ] **Scraping Logs**: Rozbudowa tabeli w DuckDB o metryki sesji (ile nowych linków dodano w danej minucie).
- [ ] **Integrity Guard**: Skrypt weryfikujący spójność bazy tagów z bazą artykułów.

---

## 🧠 Faza 2: Inteligencja i Procesowanie (NASTĘPNY KROK)

*Cel: Zamiana surowych linków w polskojęzyczną wiedzę za pomocą AI.*

- [x] **Ollama Orchestrator**: Automatyczne zarządzanie serwerem Ollama (On-Demand) i pobieranie modeli.
- [ ] **RAG Engine**: Integracja LlamaIndex z bazą wektorową (ChromaDB) dla artykułów.
- [ ] **Auto-Translation V2**: Automatyczne tłumaczenie nagłówków i streszczeń artykułów na polski przy użyciu
  `deep-translator`.
- [ ] **Semantic Filter**: Wykorzystanie modelu LLM (np. Llama 3) do odrzucania artykułów niskiej jakości ("mięso" vs "
  lorem ipsum").

---

## 📂 Faza 3: Integracja z Obsidianem (Wiki-Vault)

*Cel: Automatyczne budowanie osobistej encyklopedii.*

- [ ] **Vault Generator**: Automatyczna struktura folderów na podstawie tagów z `tags.txt`.
- [ ] **Smart Notes**: Generowanie notatek MD z podziałem na atomowe sekcje (H1-H3).
- [ ] **Knowledge Merge**: Łączenie nowej wiedzy z istniejącymi notatkami (brak duplikatów plików).
- [ ] **Auto-Linking**: Tworzenie powiązań `[[bi-directional]]` między pojęciami technicznymi.

---

## 📊 Faza 4: Monitoring i Interfejs

*Cel: Wgląd w pracę Agenta i kontrola zasobów.*

- [ ] **Dashboard**: Prosty interfejs (Streamlit) pokazujący przyrost bazy danych.
- [ ] **Resource Guard**: Monitorowanie RAM/CPU przed uruchomieniem ciężkich modeli AI.
- [ ] **Daily Summary**: Poranne powiadomienie o najciekawszych znalezionych artykułach z ostatniej nocy.

---

### 🛠️ STOS TECHNOLOGICZNY (Status: PANCERNY)

- **Język**: Python 3.14 (Venv)
- **Baza**: DuckDB (SQL)
- **Scraper**: Playwright (Headless)
- **Sterowanie**: GNU Make (Zmodularyzowany)
- **AI**: Ollama (Llama 3 + Nomic-Embed)

---

Proponowany schemat działania (The Pipeline)
Etap 1: Ingestion (Scraper)

Zadanie: Znajdź nowe linki, tytuły i tagi.

Status w bazie: pending.

Częstotliwość: Kilka razy dziennie (automatycznie).

Etap 2: Enrichment (Processor AI)

Zadanie: Pobierz pełną treść (jeśli potrzebna), przetłumacz, wygeneruj punkty.

Status w bazie: processed.

Częstotliwość: Raz na dobę lub na żądanie (make agent-process).

Etap 3: Export (Obsidian)

Zadanie: Weź rekordy processed i stwórz z nich piękne notatki .md.

Status w bazie: exported.
