# Future SDK Boundary

Doctor link P5 does not introduce a stable SDK.

This document describes what future SDK work may cover and what is intentionally not promised by P5.

## Possible future SDK areas

A future SDK may include:

- collector adapter APIs;
- evidence writer helpers;
- handoff profile registration;
- verification adapter interfaces;
- diagnostic package schema helpers;
- project template generators.

## Not promised in P5

P5 does not provide:

- runtime plugin loading;
- third-party adapter discovery;
- cloud adapter marketplace;
- external account integration;
- paid service integrations;
- stable public SDK compatibility guarantees.

## Current extension path

Use configuration files and CLI commands:

- `.doctorlink/diagnosis.yml`
- `.doctorlink/reproduce.yml`
- `.doctorlink/test-matrix.yml`
- `.doctorlink/collect.yml`
- `.doctorlink/verification.yml`

## Safety rule

Future SDK work must preserve local-first behavior, privacy review, and verification-first closure.
