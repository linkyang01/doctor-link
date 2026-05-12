# Doctor link Product Design

## 1. Product positioning

Doctor link is an independent universal diagnostic and AI collaboration tool.

It is designed to help non-programmer users collect evidence, plan tests, record failures, generate diagnosis reports, and create AI-ready debugging tasks.

Doctor link is not tied to Vly. Vly is only the first real-world adapter.

## 2. Core users

| User | Need |
|---|---|
| Non-programmer builder | Describe bugs clearly to AI coding tools |
| AI coding workflow user | Provide structured context to Codex / AI Code |
| Developer | Get reproducible reports and evidence |
| Project owner | Track quality over time |

## 3. Core value

Doctor link turns vague issue reports into structured diagnostic packages.

Before:

> This file cannot play.

After:

- environment;
- file information;
- logs;
- reproduction steps;
- test matrix;
- failure category;
- AI task prompt;
- verification checklist.

## 4. Product principles

1. Independent from any single app.
2. Useful before the target app is complete.
3. Evidence first, guesses later.
4. Designed for AI collaboration.
5. Structured output in Markdown and JSON.
6. Adapter-based architecture.
7. Start as CLI, later add local Web UI.

## 5. First scenario: Vly Core Proof

Doctor link helps test whether Vly can become an all-in-one media player.

It will:

- scan `VlyTestLibrary`;
- identify missing sample categories;
- generate playback test plans;
- collect test results;
- generate Doctor reports;
- generate AI / Codex tasks;
- decide Go / No-Go for the next Vly stage.
