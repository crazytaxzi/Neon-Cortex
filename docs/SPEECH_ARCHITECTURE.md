# Speech Architecture

## Minimum acceptable mouth

Neon Cortex uses `Qwen/Qwen3-TTS-12Hz-0.6B-Base` as the minimum speech-output model.

This is the floor because it is the smallest official Qwen3-TTS checkpoint that supports rapid voice cloning from reference audio. `CustomVoice` checkpoints are not an acceptable substitute for the floor because they use bundled speaker identities rather than arbitrary user-provided voice cloning.

## Acceptance requirements

The mouth must:

- run locally in its own service;
- support voice cloning from a short reference recording;
- preserve Cinder's intended wording rather than rewriting it;
- sound conversational rather than like an automated call-center voice;
- support streaming or sufficiently low-latency playback for interruption-capable dialogue;
- expose failure and timing information to the supervisor;
- remain replaceable by a higher-quality model without changing the main-character interface.

## Quality gate

The 0.6B Base checkpoint is the floor, not an automatic final choice. It must pass an A/B listening test using the same Cinder reference voice and script against the 1.7B Base checkpoint.

Promote the 1.7B Base checkpoint only when the improvement in naturalness, emotional continuity, pronunciation, or clone fidelity is clearly worth its additional memory and latency.

## Reference-audio rule

A cloned voice is only as good as its reference. Use a clean recording with:

- one speaker;
- no music, effects, reverb, clipping, or background chatter;
- natural conversational delivery;
- an accurate transcript;
- enough variation to expose cadence without exaggerated acting.

Maintain multiple approved reference clips for neutral, amused, irritated, urgent, and intimate delivery. The speech service may select an approved reference profile, but it may not invent or modify Cinder's final text.

## Role boundary

The mouth speaks. It does not reason, summarize, sanitize, embellish, or decide what Cinder meant.
