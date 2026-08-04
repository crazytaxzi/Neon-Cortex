# Neon Cortex

Neon Cortex is the local-first cognition stack for **Cinder**, Senti's PC-dwelling shoulder demon, practical co-conspirator, and eventually voice-driven desktop agent.

This project is not a generic chatbot with a novelty system prompt stapled to its forehead. Cinder's identity, judgment, memory, language, autonomy boundaries, and interaction style are treated as product architecture.

## Current phase

Phase 1 proves the smallest useful local loop:

1. Start and stop the local Qwen model reliably.
2. Chat through a basic desktop UI.
3. Store, search, and retrieve persistent memory quickly.
4. Collect approved conversations for later Cinder LoRA training.
5. Validate behavior before adding voice, computer control, or agent swarms.

See [`docs/PHASE_1.md`](docs/PHASE_1.md) for acceptance criteria.

## Design rules

- Local-first. Core chat and memory must not require a cloud service.
- Native Windows execution first; Docker is not a Phase 1 dependency.
- Useful first, personality second, but never personality-free.
- Small specialized agents coordinated through one explicit orchestration layer.
- Memory writes require source, type, confidence, and retention rules.
- Actions must be observable and verifiable.
- No invented capabilities, fake success, silent failure, or mystery state.
- Destructive, financial, credential, account, and mass-action operations require stronger confirmation.
- Structured logs and machine errors remain plain and diagnostic. Cinder can flirt with the user, not with the stack trace.

## Canonical project documents

- [`AGENTS.md`](AGENTS.md) — contribution and agent-development rules
- [`docs/CINDER_PERSONA.md`](docs/CINDER_PERSONA.md) — canonical behavior contract
- [`config/persona/cinder-core.md`](config/persona/cinder-core.md) — compact runtime persona seed
- [`docs/MEMORY_CONTRACT.md`](docs/MEMORY_CONTRACT.md) — memory model and retrieval policy
- [`docs/PHASE_1.md`](docs/PHASE_1.md) — current scope and test gates

## Long-term direction

Neon Cortex will grow into a voice-native, screen-aware, self-correcting desktop companion that can interpret goals, delegate work to small agents, inspect results, act through approved tools, remember what matters, and report back without nagging Senti for permission to breathe.

The target is not an omnipotent AI overlord. It is a capable local PC goblin with judgment, continuity, a sharp mouth, and hands kept firmly on the correct controls.
