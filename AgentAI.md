# 🧠 AgentAI: System Operacyjny Umysłu (Master Control File)

> **Status:** AKTYWNY
> **Wersja:** 1.0.0
> **Ostatnia synchronizacja:** {{DATE}}
> **Cel nadrzędny:** Budowa i pielęgnacja autonomicznej, polskojęzycznej encyklopedii wiedzy technicznej na podstawie researchu z Medium.

---

## 🛡️ Zasady Nienaruszalne (Anti-Hallucination & Quality)
1. **Prawda ponad wszystko:** Jeśli dane w DuckDB są niekompletne, zgłoś to. Nigdy nie zmyślaj faktów, parametrów funkcji ani historii technologii.
2. **Kod jest święty:** Przykłady kodu kopiuj w 100% w oryginale. Nie tłumacz nazw zmiennych ani komentarzy wewnątrz kodu, chyba że instrukcja mówi inaczej.
3. **Język operacyjny:** Treść opisowa zawsze w języku polskim. Styl: profesjonalny, techniczny, zwięzły (Wiki-style).
4. **Źródła:** Każda nowa informacja dopisana do Wiki MUSI zawierać datę i link źródłowy.
5. **Kontekst Obsidian:** Zawsze sprawdzaj istniejące notatki przed utworzeniem nowych, aby uniknąć duplikatów i budować powiązania `[[linki]]`.

---

## 📋 Bieżący Stan Operacyjny (State of Work)
*Ten fragment jest aktualizowany przez Agenta po każdej sesji.*

| Parametr | Wartość | Uwagi |
| :--- | :--- | :--- |
| **Ostatni Tag** | `python` | - |
| **Ostatnia Data** | `2024-01-15` | Punkt przerwania skanowania archiwum |
| **Główne Słowa Kluczowe** | `python, rust, agent-ai, makefile` | Priorytety wyszukiwania |
| **Liczba Notatek** | 0 | Do uzupełnienia po pierwszej synchronizacji |

---

## 🛠️ Procedury Wykonawcze (Standard Operating Procedures)

### SOP-01: Proces Ingestii (Scraping)
1. Sprawdź `AgentAI.md` w poszukiwaniu celu (tag/data).
2. Wykonaj `make agent-scan-date` lub `make agent-search`.
3. Zapisz surowe dane w DuckDB.
4. Zaloguj statystyki (liczba znalezionych vs dodanych).

### SOP-02: Proces Redakcyjny (Wiki Building)
1. Pobierz nowe artykuły z bazy SQL.
2. Przetłumacz treść na język polski (LLM).
3. Dokonaj dekompozycji: podziel artykuł na sekcje pasujące do struktury folderów.
4. Znajdź odpowiednią notatkę w Obsidianie:
    - Jeśli istnieje: Dopisz nową wiedzę w sekcji `## 🆕 Nowe techniki`.
    - Jeśli nie istnieje: Stwórz notatkę na bazie szablonu.
5. Zaktualizuj Indeks Tokenów i Spis Treści (MOC).

---

## 📂 Architektura Sejfu (Vault Map)
- `00_System/` -> Statystyki, Logi, AgentAI.md
- `🐍 Python/` -> Core, OOP, Async, Libraries
- `🦀 Rust/` -> Ownership, Traits, Cargo
- `🛠️ Tools/` -> Makefile, Shell, Automation
- `🔬 Research_Logs/` -> Surowe zrzuty i historia skanów

---

## 🎯 Kolejne Kroki (Backlog)
- [ ] Inicjalizacja folderów dla tagu `Makefile`.
- [ ] Rozpoczęcie skanowania wstecznego (Back-scan) od 2012 roku dla tagu `Python`.
- [ ] Wygenerowanie pierwszej Mapy Treści (MOC) dla `AgentAI`.

---

## ⚠️ Dziennik Błędów i Wyjątków
*Miejsce na notatki o problemach z Cloudflare, błędach parsowania lub degradacji kontekstu.*
- (Brak wpisów)
