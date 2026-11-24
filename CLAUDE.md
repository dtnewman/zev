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
- Concrete providers: `openai/`, `gemini/`, `ollama/`, `azure_openai/`, `anthropic/`
- No provider SDKs: every provider calls its HTTP API with `urllib` (shared helper in `llms/http.py`); keep it that way rather than adding dependencies
- `OllamaProvider` and `AzureOpenAIProvider` both extend `OpenAIProvider` (Chat Completions with a strict JSON schema); Azure's optional `azure-identity` extra is only for Entra ID tokens
- All providers return `OptionsResponse` (dataclass in `llms/types.py`, with the shared `OPTIONS_RESPONSE_SCHEMA`) with up to 3 `Command` objects, each having `command`, `short_explanation`, `is_dangerous` and `dangerous_explanation` fields

**Config** (`src/zev/config/`):
- Stored as `KEY=value` lines in the platform user data dir (`paths.py`; legacy `~/.zevrc` is migrated); parsed by `read_config_file()` and loaded via singleton `Config` class
- Interactive setup flow in `config/setup.py` using questionary prompts
- `config/types.py` defines `SetupQuestion` dataclass with optional `follow_up_questions` for provider-specific settings

**History:** Stored as JSONL in the user data dir, max 100 entries. The `--recent` flag opens an interactive selector over past queries.

**Code style:** 120-char line length, ruff for linting (import sort only via `I001`), isort with black profile. Match the style of surrounding code.
