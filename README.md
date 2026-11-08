# RBIQA

Grounded question answering over RBI Master Directions (NBFCs and Payments Banks), with an evaluation pipeline that measures retrieval and answer quality.

## Quick start

```bash
make setup     # installs dependencies and creates data directories
cp .env.example .env   # then add GEMINI_API_KEY
make check     # verifies the environment
make all       # lint, type-check, and tests
```
