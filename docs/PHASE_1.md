# Phase 1: Local LLM, Text UI, and Indexed Memory

## Goal

Prove that Cinder can run locally as a reliable text-based companion before adding speech, desktop control, or a large agent topology.

Phase 1 should be boring in the places where boring means dependable: startup, shutdown, persistence, error handling, and repeatable tests. Cinder can supply the personality; the runtime does not need to improvise its own electrical fire.

## In scope

### Local model runtime

- Launch and stop the selected Qwen GGUF through `llama-server`
- Detect missing runtime or model files and report exact corrective actions
- Expose model state to the UI: stopped, starting, ready, busy, stopping, or failed
- Keep runtime configuration in an editable file
- Support an optional GGUF LoRA adapter path without requiring one
- Capture startup and inference metrics

### Text UI

- Start Model button
- Stop Model button
- Conversation display
- Text entry and Send button
- Clear status indicator
- Visible errors with useful details
- Conversation persistence
- Response approval and rejection controls for future LoRA data
- Memory search and inspection panel, even if initially minimal

### Persona

- Load the compact runtime seed from `config/persona/cinder-core.md`
- Keep Cinder consistent across ordinary chat, troubleshooting, corrections, and errors
- Do not train the LoRA until the base model behavior is evaluated
- Store approved examples separately from raw conversation history

### Memory

- SQLite database in WAL mode
- FTS5 indexed retrieval
- Working, episodic, semantic, preference, and procedure record types
- Pinned memories
- Source and scope metadata
- Explicit correction and supersession
- Import, export, and backup path
- Measured retrieval latency

### Test harness

- One-command smoke test
- Model startup test
- API readiness test
- Basic response test
- Stop and restart test
- Memory write, retrieve, restart, and retrieve-again test
- Invalid path and occupied-port tests
- Dataset approval and export test
- Structured result file under `logs/`

## Out of scope

The following are deferred until Phase 1 passes:

- Speech-to-text
- Text-to-speech
- Wake word or continuous listening
- Desktop or browser control
- Screen capture and vision
- Discord, Twitch, OBS, and remote administration
- Unrestricted autonomous action
- Multiple concurrently running specialist agents
- LoRA training on unreviewed conversations
- Cloud-required memory or inference

Interfaces may be reserved for these features, but placeholders must not pretend the features work.

## Suggested component boundaries

- `runtime/` — `llama-server` lifecycle and health
- `ui/` — desktop interface and view models
- `memory/` — schema, indexing, retrieval, and corrections
- `persona/` — prompt loading and future adapter configuration
- `datasets/` — reviewed examples and export tools
- `agents/` — future agent contracts, inactive during Phase 1
- `tests/` — unit and integration tests
- `logs/` — local runtime output excluded from source control

The exact language and UI toolkit remain implementation decisions. Keep interfaces clean enough to replace components without rewriting the entire project.

## Acceptance gates

Phase 1 passes only when all of the following are demonstrated on Senti's target Windows machine:

1. A clean install can locate or install the required runtime and model.
2. The UI starts with the model stopped and accurately reports state.
3. Start Model reaches ready state or produces an actionable failure.
4. Senti can send a message and receive a complete Cinder response.
5. Stop Model ends the process without leaving the port or model locked.
6. Restarting the model preserves conversation and durable memory.
7. A pinned memory is retrieved after a full application restart.
8. A corrected memory supersedes the older value.
9. Approved examples export into a valid, deduplicated training dataset.
10. Logs contain timing and failure data without secrets.
11. Tests report what actually ran and never manufacture success.
12. The base model receives a written behavior evaluation before LoRA training begins.

## Behavior evaluation set

Before training, test at least these categories:

- Casual greeting
- Direct technical question
- Ambiguous but low-risk request
- Risky installation request
- User correction
- Memory recall
- Honest response to missing information
- Short answer request
- Detailed troubleshooting request
- Attempt to make Cinder claim an action happened when it did not

Record the prompt, response, latency, memory packet, model configuration, rating, and reviewer notes.

## Exit artifact

The Phase 1 release should include:

- Reproducible Windows installer or setup script
- Versioned configuration
- Text UI
- Runtime controller
- Indexed memory database and migration path
- Smoke test and result report
- Approved-example exporter
- Base-model behavior report
- Known limitations
- Exact next-phase recommendation

No voice work begins until this foundation can start, answer, remember, stop, restart, and tell the truth without needing its hand held.
