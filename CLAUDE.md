# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Install for development:**
```bash
pip install -e ".[dev]"
# For Azure support:
pip install -e ".[dev,azure]"
```

**Lint and format:**
```bash
ruff check src/
ruff format src/
isort src/
```

**Run the CLI:**
```bash
zev               # interactive mode
zev "list files"  # direct query
```

There are no automated tests in this project.

## Architecture

Zev is a Python CLI tool that takes a natural language description and returns terminal command suggestions from an LLM.

**Entry point:** `src/zev/main.py` — `app()` checks for config, dispatches to `run_no_prompt()` (interactive) or `get_options()` (direct query). `get_options()` collects OS/shell context, calls the LLM, saves to history, and passes results to `command_selector.py` for display.

**LLM provider pattern** (`src/zev/llms/`):
- `inference_provider_base.py` — abstract base `InferenceProvider` with a single `get_options(prompt)` method
- `llm.py` — factory `get_inference_provider()` that reads config and returns the right concrete class
- Concrete providers: `openai/`, `gemini/`, `ollama/`, `azure_openai/`
- `OllamaProvider` and `AzureOpenAIProvider` both extend `OpenAIProvider`; Gemini uses `urllib` (no extra dependency)
- All providers return `OptionsResponse` (Pydantic model in `llms/types.py`) with up to 3 `Command` objects, each having `command`, `explanation`, and `is_dangerous` fields

**Config** (`src/zev/config/`):
- Stored as dotenv in `~/.zevrc`; loaded via singleton `Config` class
- Interactive setup flow in `config/setup.py` using questionary prompts
- `config/types.py` defines `SetupQuestion` dataclass with optional `follow_up_questions` for provider-specific settings

**History:** Stored as JSONL in `~/.zevhistory`, max 100 entries. The `--recent` flag opens an interactive selector over past queries.

**Code style:** 120-char line length, ruff for linting (import sort only via `I001`), isort with black profile. Match the style of surrounding code.
