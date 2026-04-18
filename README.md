# agentai

[![PyPI - Version](https://img.shields.io/pypi/v/agentai.svg)](https://pypi.org/project/agentai)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/agentai.svg)](https://pypi.org/project/agentai)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install agentai
```

## License

`agentai` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

# Założenia Projektu

# Projekt: Personal Research Agent (PRA) - "Knowledge Weaver"

## 🎯 Cel Projektu
Stworzenie autonomicznego systemu opartego na lokalnych modelach AI (Gemma 2), który monitoruje wybrane źródła (Medium.com), gromadzi wiedzę techniczną i buduje hierarchiczną bazę wiedzy w formacie Markdown, kompatybilną z aplikacją Obsidian.

## 🧠 Architektura AI
* **Silnik:** Ollama działająca lokalnie na macOS (M1 Pro 32GB).
* **Modele:** * **Gemma 2 2B (Lekka):** Szybka klasyfikacja linków, filtrowanie spamu, proste tagowanie.
    * **Gemma 2 27B (Ciężka):** Głęboka analiza, tłumaczenie (EN -> PL), restrukturyzacja plików, synteza wiedzy.
* **Baza danych:** * **DuckDB:** Metadane, statusy linków, kolejka zadań, logi.
    * **ChromaDB:** Wyszukiwanie semantyczne (wektorowe), sprawdzanie duplikatów wiedzy.

## 🛠️ Moduły Systemu
1.  **Monitor (Scraper):** Playwright z zapisaną sesją (auth), omijanie paywalli, pobieranie treści + obrazków.
2.  **Orkiestrator (Resource Guard):** Monitoruje `psutil` (CPU/GPU), wstrzymuje prace przy renderowaniu wideo/użyciu Final Cut.
3.  **Translator & Synthesizer:** Tłumaczenie treści z zachowaniem oryginalnego kodu źródłowego.
4.  **Librarian (Menedżer plików):** Zarządzanie strukturą katalogów w Obsidian Vault, obsługa linków relatywnych do grafik.

## 📂 Zasady Zarządzania Wiedzą
* **Język:** Treść merytoryczna po polsku, kod i komentarze techniczne w oryginale (EN/PL mix).
* **Struktura:** Hierarchiczna (Katalogi: Python, Rust, Makefile, Shell).
* **Prywatność:** 100% lokalnie (chyba że wymuszone API Gemini przy braku zasobów).
* **Aktualizacja:** Nowa wiedza oznaczana tagiem HTML `<mark>` lub komentarzem czasowym.
