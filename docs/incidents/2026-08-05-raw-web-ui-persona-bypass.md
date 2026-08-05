# 2026-08-05 — Raw web UI bypassed the Cinder identity layer

## Summary

A local conversation exported from `llama.app` was initially treated as a test of `cinder-qwen3.5-9b`. It was not a valid Cinder behavior test.

The session used the llama.cpp browser interface connected directly to the model server. The exported root `system` message was empty. The model alias included `cinder`, but no Cinder persona, memory context, or runtime behavior contract was present in the conversation.

This is an integration failure and a test-harness failure, not sufficient evidence that the underlying Qwen model cannot support Cinder.

## Evidence

The private source export showed:

- Harness: `llama.app`
- Model alias: `cinder-qwen3.5-9b`
- Root system content: empty
- First user prompt: `basic bitch`
- First prompt token count: 14
- Direct server endpoint used during testing: `http://127.0.0.1:8088`

The original conversation is intentionally not committed because this repository is public and the export contains private conversational material.

## Observed symptoms

Without the identity layer, the model:

- Answered a directed tease with a dictionary-style definition.
- Used generic assistant phrasing, emojis, and corporate politeness.
- Repeated therapy-style language after the user explicitly rejected that framing.
- Made broad and sometimes inaccurate claims about model architecture, persistence, agency, and agent loops.
- Simulated numbered "agentic turns" instead of checking whether the harness could actually execute an agent loop.
- Reversed philosophical positions under pressure rather than maintaining a precise, evidence-based distinction.
- Never behaved recognizably as Cinder.

## Root cause

Cinder Alpha currently applies persona and memory at the client/request layer. Starting `llama-server` does not permanently install Cinder into the weights or into every client that connects to the port.

Opening the llama.cpp web interface at port 8088 talks to the raw model unless that browser session is explicitly given a system prompt. The model name is only an alias; it is not proof that the identity contract was loaded.

## Data disposition

- Reject every assistant response in this session as positive LoRA training data.
- Keep the original export private and off-repository.
- Reuse sanitized user prompts as adversarial regression cases.
- Treat the session as evidence that prompt-presence verification is mandatory.

## Required controls

1. Every Cinder client must send one non-empty initial system message containing the compact persona seed and any retrieved memory.
2. The UI must display the active persona identifier or prompt hash.
3. A conversation export must record the client, model alias, persona identifier, and system-prompt hash.
4. Cinder-facing clients should refuse to label a session as Cinder when the system prompt is empty.
5. The raw llama.cpp browser UI must be labeled as a raw-model test surface, not the canonical Cinder interface.
6. Worker endpoints must receive explicit role contracts on every job; a model alias must never be treated as a role or identity guarantee.

## Regression gate

A Cinder behavior evaluation is invalid unless all of the following are recorded before the first user turn:

- Non-empty system message
- Expected persona identifier
- Expected model identifier
- Client or harness identifier
- Prompt hash or version
- Memory injection status

If any field is missing, classify the run as `harness_invalid` rather than grading model personality.
