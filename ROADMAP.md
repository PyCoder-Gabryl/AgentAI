# 🗺️ Roadmap: Knowledge Weaver (AgentAI)

## 🎯 Faza 0: Fundamenty (ZAKOŃCZONE)
- [x] Konfiguracja środowiska Python 3.14 (venv).
- [x] Inicjalizacja bazy wiedzy DuckDB (`articles`).
- [x] **Scraper V2**:
  - [x] Obsługa trybów: `ARCHIVE`, `SEARCH`, `LIST`, `ALL_LISTS`, `SINGLE`.
  - [x] Automatyzacja "Show More" i scrollowania.
  - [x] Mechanizm zachowywania sesji (Playwright Context).
- [x] **Sterowanie (Makefile)**:
  - [x] Polecenia do skanowania po dacie, frazie i URL.
  - [x] Narzędzia analityczne (`db-stats`, `db-trends`).
  - [x] Moduł czyszczący śmieci (`db-clean-trash`) z raportowaniem.

---

## 🛠️ Faza 1: Autonomia i Zarządzanie Stanem (TERAZ)
*Cel: Sprawić, by Agent wiedział, co zrobił i nie powielał pracy.*

- [ ] **AgentAI.md (Master Control File)**:
  - Implementacja pliku w Obsidianie jako "Single Source of Truth".
  - Definicja zasad nienaruszalnych (Anti-Hallucination Protocol).
- [ ] **Inteligentna Pamięć (DuckDB)**:
  - [ ] **Tabela `scan_history`**: Rejestr obsłużonych dat i tagów (Smart History).
  - [ ] **Tabela `scraping_logs`**: Szczegółowe metryki każdej sesji (duration, success_rate, total_seen).
- [ ] **Automatyzacja Cykliczna**:
  - [ ] **Multi-Tag Loop**: Kolejka tagów "Core" do codziennego skanowania.
  - [ ] **Scheduler**: Skrypt do uruchamiania nocnego (po północy).
  - [ ] **Archive Catch-up**: Algorytm nadrabiania historii od 2012 roku w oknach czasowych niskiego priorytetu.

---

## 🧠 Faza 2: Inteligencja i Procesowanie (RAG)
*Cel: Zamiana surowych linków w polskojęzyczną wiedzę.*

- [ ] **Silnik AI (Ollama)**:
  - [ ] Konfiguracja modelu 2B (klasyfikacja) i 27B (tłumaczenie/synteza).
  - [ ] Integracja LlamaIndex z ChromaDB (baza wektorowa).
- [ ] **Redakcja Tekstu**:
  - [ ] **Auto-Translation**: Tłumaczenie opisów przy zachowaniu oryginalnego kodu.
  - [ ] **Dekompozycja**: Podział artykułów na atomowe notatki według nagłówków H1-H3.
- [ ] **Discovery Engine**:
  - [ ] Wyciąganie "Related Tags" i sugerowanie nowych obszarów badań.
  - [ ] Ranking ważności źródeł na podstawie "mięsa" (wartościowej treści).

---

## 📂 Faza 3: Integracja z Obsidianem (Wiki-Vault)
*Cel: Automatyczne budowanie Twojej osobistej encyklopedii.*

- [ ] **Vault Generator**:
  - [ ] Automatyczna struktura folderów (`[Tag]/Core`, `[Tag]/Advanced`).
  - [ ] Generowanie Map Treści (MOC) i indeksów.
- [ ] **Smart Notes**:
  - [ ] **Versioning & Sourcing**: Dopiski z datą i linkiem (ukryte w Callouts).
  - [ ] **Knowledge Merge**: Łączenie nowej wiedzy z istniejącymi notatkami zamiast tworzenia duplikatów.
  - [ ] **Auto-Linking**: Tworzenie powiązań `[[pojęć]]` wewnątrz tekstów.
- [ ] **Sync Command**: Polecenie `make agent-sync` (pełna ścieżka: Link -> SQL -> AI -> MD).

---

## 📊 Faza 4: Interfejs i Monitoring
*Cel: Wgląd w pracę Agenta i kontrola zasobów.*

- [ ] **Streamlit Dashboard**:
  - [ ] Wykresy przyrostu wiedzy (dzień/miesiąc/rok).
  - [ ] Zarządzanie listą tagów i priorytetów.
- [ ] **Resource Guard**: Monitorowanie obciążenia systemu przed startem ciężkich zadań AI.
- [ ] **Newsletter Agenta**: Poranne podsumowanie (Daily Summary) o nowych odkryciach i trendach.
- [ ] **Moduł Audytora**: Automatyczna kontrola jakości notatek i czyszczenie bazy wektorowej.

---

### 📝 Standard Operacyjny Notatki (Wiki-Style)
- **Tytuł**: Angielskie pojęcie techniczne (np. `Asyncio_Loops.md`).
- **Język**: Opis polski, merytoryczny, zwięzły.
- **Kod**: Oryginalne snippety, nazewnictwo zmiennych bez zmian.
- **Źródła**: Pełna transparentność (Data + URL) w każdej dopisanej sekcji.
