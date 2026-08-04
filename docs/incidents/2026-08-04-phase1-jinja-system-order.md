# Phase 1 Incident: Qwen Jinja System-Message Ordering

## Observed behavior

The first local chat response completed successfully, but the next response after durable memory was added failed with HTTP 500:

`Jinja Exception: System message must be at the beginning.`

A separate launch attempt from the extracted source folder also failed because its uninstalled `config/settings.json` contained blank runtime and model paths.

## Root cause

The UI constructed the request as:

1. persona system message
2. retrieved-memory system message
3. recent user and assistant messages

The Qwen3.5 llama.cpp chat template accepts the system role only at the beginning and does not accept a second system message. The model and GGUF were healthy; request assembly was wrong.

## Corrective action

- Merge persona and retrieved memory into one first system message.
- Add runtime and model auto-discovery under both the current project root and `%LOCALAPPDATA%\Cinder_Alpha`.
- Reduce the default output ceiling from 768 to 384 tokens.
- Lower temperature from 0.72 to 0.65.
- Tighten the runtime persona against unsolicited Markdown, fake status blocks, canned greetings, and long scene-setting.
- Preserve the model and SQLite memory database during patching.

## Validation required

After applying hotfix 0.1.1:

1. Start the model.
2. Ask a normal question with no retrieved memory.
3. Pin a relevant memory.
4. Ask a question that retrieves it.
5. Confirm no HTTP 500 occurs and only one system message is sent.
6. Confirm restart preserves the pinned memory.

The initial answer was correctly rejected from LoRA data because it was verbose and formatted as a fake status report. A technically successful generation is not automatically good training material.
