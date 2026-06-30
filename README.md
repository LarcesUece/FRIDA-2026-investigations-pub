FRIDA 2026 - INVESTIGATIONS
---------------------------

Como configurar e rodar o projeto:

1. Clonar o repositório.

2. Instalar dependências:
   npm install

3. Instalar bibliotecas de suporte (CSV):
   npm install papaparse
   npm install -D @types/papaparse

4. Rodar o servidor:
   npm run dev
# frida-2026-investigations

## commands to run the test:
```bash
uv sync
uv run pytest -k anonymization -s
uv run python -m app.tests.benchmark_anonymization
