# Python MVP

This is the temporary implementation path while the local machine does not have a Next.js project environment ready.

## Goal

Validate the content engine before building the web UI.

Input:

```text
Book name
```

Output:

```text
Book recall
Book profile
Narrative outline
Node-by-node script
Factuality report
Quality report
```

## Architecture

```text
CLI
-> Content Orchestrator
-> LLM Client
-> Book Recall
-> Profile Generator
-> Outline Generator
-> Node Content Generator
-> Factuality Reviewer
-> Node Reviser, when factuality fails
-> Quality Reviewer
-> JSON Result
```

## Run With Mock Data

Use mock mode to verify the pipeline without an API key:

```bash
python -m mvp_python.cli --book 倚天屠龙记 --mock
```

In the current Codex desktop environment, Python is available at:

```text
C:\Users\ning2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

So the local command is:

```powershell
& 'C:\Users\ning2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m mvp_python.cli --book 倚天屠龙记 --mock
```

## Run With DeepSeek

Create `.env.local` in the project root:

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_MODEL=deepseek-v4-flash
```

Then run:

```bash
python -m mvp_python.cli --book 倚天屠龙记 --duration 12
```

DeepSeek is the temporary provider while OpenAI API credits are unavailable.

## Switch Back To OpenAI Later

Update `.env.local`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4.1
```

The Python MVP reads `.env.local` automatically. Do not commit real keys.

Then run:

```bash
python -m mvp_python.cli --book 倚天屠龙记 --duration 12
```

## Save Result

```bash
python -m mvp_python.cli --book 倚天屠龙记 --mock --out outputs/yitian.json
```

## Fact Probe

Before generating a story script, test whether the active model knows the original work's factual structure:

```bash
python -m mvp_python.fact_probe --book 倚天屠龙记 --out outputs/yitian_fact_probe.md
```

The fact probe asks for:

- Characters.
- Events.
- Timeline.
- Possible risky facts.

Use this to decide whether the model can safely enter the narration pipeline, or whether a human-confirmed fact pack is required first.

## Current Generation Flow

The MVP generation flow is now:

```text
Book
-> Recall
-> Profile
-> Outline
-> Nodes
-> Factuality Review
-> Node Revision, max 2 retries
-> Quality Review
```

`Profile`, `Outline`, and `Nodes` all receive the recall facts. The profile is not treated as the only source of truth.

Each node is structured:

```json
{
  "node_id": "",
  "title": "",
  "source_scenes": [],
  "required_facts": [],
  "causal_context": "",
  "emotional_context": "",
  "narration": "",
  "uncertainty_notes": []
}
```

The factuality reviewer runs before the quality reviewer. It checks whether the generated nodes invented important events, changed relationships, changed motivations, reversed causality, moved later events earlier, or mixed scenes together.

If factuality fails, the orchestrator asks the model to revise the nodes and then reviews factuality again. It stops after 2 retries to avoid loops.

## Scope

This version intentionally does not include:

- Web UI.
- Database.
- User accounts.
- TTS.
- RAG.
- LangChain.

It only tests whether the generation pipeline can produce better story-first content.
