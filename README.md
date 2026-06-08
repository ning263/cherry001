# Cherry

AI-assisted literary experience prototype.

## Current MVP

The active MVP is a Python content-engine prototype in `mvp_python/`.

It validates this pipeline:

```text
Book
-> Recall
-> Profile
-> Outline
-> Nodes
-> Factuality Review
-> Quality Review
```

Run with mock data:

```powershell
& 'C:\Users\ning2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m mvp_python.cli --book 倚天屠龙记 --mock
```

Run with the configured LLM provider:

```powershell
& 'C:\Users\ning2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m mvp_python.cli --book 倚天屠龙记 --duration 6 --out outputs\yitian_deepseek_v2.json
```

See `docs/PYTHON_MVP.md` for details.
