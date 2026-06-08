# Decision 0001: Static MVP Workbench

## Status

Accepted

## Context

The project needs to validate whether it can make a book feel alive before building a larger app surface.

The immediate risk is not technical scale. The risk is that generated content still sounds like a summary, lecture, or essay.

## Decision

Build the first MVP as a zero-dependency static workbench in `mvp/`.

The prototype should require structured content inputs before generating a talk track:

- Shallow summary to reject.
- Story archetype.
- Protagonist lens.
- Key scenes.
- Scene pressure.
- Scene turn.
- Scene consequence.
- Modern resonance.
- Open question.

## Rationale

This keeps the prototype focused on the content engine rather than app infrastructure.

It also makes failures easier to diagnose. If a generated draft lacks story force, the missing scene, pressure, or consequence should be visible in the input structure.

## Non-Goals

- No backend.
- No account system.
- No model API integration.
- No large book library.
- No final product UI.
