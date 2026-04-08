# frida-2026-investigations

## commands to run the test:
```bash
uv sync
uv run pytest -k anonymization -s
uv run python -m app.tests.benchmark_anonymization