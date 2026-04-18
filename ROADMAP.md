# 🗺️ Roadmap Projektu: Knowledge Weaver

## Faza 1: Fundamenty (Środowisko i Scraper)
- [x] Konfiguracja środowiska Python 3.14 (venv).
- [ ] Instalacja i konfiguracja Ollama (test modeli Gemma 2 2B i 27B).
- [ ] Implementacja Playwright z obsługą logowania do Medium.com.
- [ ] Utworzenie bazy DuckDB dla statusów linków (Visited / Pending / Irrelevant).
- [ ] Skrypt `launchd` do cyklicznego uruchamiania monitora.

## Faza 2: Inteligencja (RAG i Przetwarzanie)
- [ ] Integracja LlamaIndex z ChromaDB (lokalna baza wektorowa).
- [ ] Implementacja "Lekkiego Agenta" (2B) do filtrowania tematów.
- [ ] Implementacja "Ciężkiego Agenta" (27B) - prompt engineering dla tłumaczeń i streszczeń.
- [ ] Logika zachowania kodu: Wyciąganie bloków `code` przed tłumaczeniem i przywracanie ich po procesie.

## Faza 3: Zarządzanie Plikami (Integracja Obsidian)
- [ ] Skrypt budujący strukturę katalogów (Vault Generator).
- [ ] Automatyczne generowanie `index.md` (Table of Contents) dla każdego działu.
- [ ] System obsługi grafik (pobieranie lokalne i linkowanie relatywne).
- [ ] Funkcja "Knowledge Merge" - sprawdzanie podobieństwa nowej treści do istniejącej przed zapisem.

## Faza 4: Interfejs i Kontrola
- [ ] Budowa prostego UI w Streamlit (ustawianie priorytetów %, podgląd kolejki).
- [ ] Implementacja Resource Guard (sprawdzanie obciążenia CPU przed startem ciężkich zadań).
- [ ] Moduł "Audytora" - cotygodniowe przeglądanie plików pod kątem zbyt dużej objętości.
- [ ] System powiadomień porannych (Daily Summary).

## Faza 5: Bezpieczeństwo i Optymalizacja
- [ ] System automatycznego backupu (pakowanie starej wersji Vault przed przebudową).
- [ ] Optymalizacja promptów w celu redukcji halucynacji.
- [ ] Testy stabilności przy dużym obciążeniu RAM.
