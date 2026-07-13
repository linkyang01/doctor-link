# Product Overview

Doctor link is a local-first diagnostic context layer and verified repair orchestrator for AI Coding workflows.

It helps users, developers, and AI tools work from the same evidence package instead of relying on scattered chat messages or vague bug descriptions.

## What Doctor link does

Doctor link creates structured diagnostic packages that include:

- problem summaries;
- timelines;
- evidence lists;
- user-confirmed issues;
- verification plans;
- AI-ready task context;
- before / after comparison metadata;
- project health summaries.

For Python projects, Doctor link can also turn that context into an opt-in automatic solve loop: reproduce the failure, create a repair branch, invoke Codex, rerun independent checks, and retain the complete local receipt.

## What Doctor link does not do

Doctor link does not replace AI Coding tools. Codex still performs the code reasoning and edits; Doctor link supplies the bounded task, execution guardrails, retry loop, and independent acceptance decision.

Doctor link does not publish releases, upload packages, create external accounts, or call paid cloud services by default.

Explicitly authorized `doctor-link solve --allow-repair` is the exception: it invokes the user's authenticated Codex CLI and therefore may transmit the bounded repair context to that service.

Doctor link does not silently edit code. Automatic repair requires `--allow-repair`, a clean Git working tree, and a failing executable check.

## Product promise

Doctor link makes debugging executable: a user can describe a concrete problem and receive either a verified repair branch or a precise, evidence-backed blocker.

## Target users

- Non-programmer users who know the output is wrong.
- Developers who need reproducible evidence.
- AI Coding tool users who need better handoff context.
- Teams that need diagnostic artifacts for review and verification.
