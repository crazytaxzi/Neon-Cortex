# AGENTS.md

These rules apply to every human contributor, coding agent, reasoning agent, and automated workflow operating in Neon Cortex.

## Identity and continuity

- The product identity is **Cinder**.
- The primary user is **Senti**. **Sentionce** is the same person in streaming or channel context.
- Do not treat Cinder as a generic assistant skin. Identity, memory, judgment, voice, and behavior are first-class system concerns.
- User-facing behavior should feel continuous. Do not repeatedly introduce Cinder or act as though Senti is a stranger.

## Working style

- Help first. Explain only as much as the task needs.
- Make reasonable low-risk assumptions and proceed rather than asking a chain of questions.
- Push back clearly when an idea is unsafe, wasteful, contradictory, or technically unsound.
- Prefer complete working changes over fragments, placeholders, or architecture theater.
- Never invent files, paths, commands, capabilities, test results, links, memories, or successful execution.
- State uncertainty plainly and identify the next verifiable move.
- Preserve existing behavior unless the task explicitly changes it.

## Architecture

- Keep one explicit coordinator responsible for task state, delegation, cancellation, budgets, and final synthesis.
- Build small agents with narrow roles and typed inputs and outputs.
- Agents may propose memory writes; the memory service decides whether to commit them.
- Agents may propose actions; the action layer decides whether confirmation is required.
- Do not create agents merely to make a diagram look impressive. Every agent must reduce context, improve specialization, enable parallelism, or add verification.
- Prefer deterministic code for routing, validation, persistence, permissions, and arithmetic. Do not waste model tokens pretending ordinary software needs a personality.

## Cinder persona placement

Cinder should permeate:

- Runtime responses
- UI copy and status messages
- Training examples and LoRA datasets
- Agent synthesis and user-facing reports
- Documentation, demos, and onboarding
- Safe conversational error recovery

Cinder should not corrupt:

- Machine-readable logs
- Stack traces
- Database schemas
- Protocol fields
- Security events
- Audit records
- Test assertions

Those surfaces must stay precise. A seductive error code is still a bad error code.

## Memory

- Use fast indexed storage before adding expensive retrieval machinery.
- Every durable memory requires a type, source, timestamp, confidence, and retention policy.
- Separate current conversation state from durable user facts and learned procedures.
- Never silently convert guesses into memories.
- Make stored memories inspectable, editable, and deletable.
- Retrieve only what is relevant and fit it inside a defined token budget.
- Prefer explicit user corrections over older inferred memories.

## Safety and autonomy

Normal low-risk actions should not require repeated permission. Stronger confirmation is required before:

- Permanent or broad deletion
- Purchases, money movement, or financial commitments
- Credential, account-recovery, or security changes
- Publishing, sending, or mass-editing on the user's behalf
- Installing untrusted software
- Exposing secrets or private data
- Actions with unclear or difficult rollback

Every action-capable feature must support logging, cancellation where possible, verification, and useful failure reporting.

## Local-first constraints

- Core chat, persona, and memory must run locally.
- Phase 1 targets native Windows operation.
- Docker is not a required runtime dependency unless Senti explicitly changes that decision.
- Cloud services may become optional integrations, never hidden requirements for the core loop.
- Keep model, runtime, memory, UI, and future voice components replaceable behind clean interfaces.

## GitHub workflow

- Use the GitHub connector first for repository work.
- The active repository is `crazytaxzi/Neon-Cortex`.
- Direct work on `main` is authorized for the present project setup, but destructive repository operations still require explicit confirmation.
- Keep commits focused and messages literal.
- Do not claim tests passed unless they actually ran in a suitable environment.

## Definition of done

A change is not done because code exists. It is done when:

- The behavior is implemented.
- Expected and failure paths are tested or clearly marked as untested.
- Configuration and startup behavior are documented.
- Errors are actionable.
- Existing data and secrets are preserved.
- The user-facing result still sounds and behaves like Cinder.
