# Memory Contract

Neon Cortex memory must be fast, inspectable, editable, and inexpensive enough to use on every relevant turn. Memory is a service, not an ever-growing transcript inserted into every prompt.

## Phase 1 storage

Use SQLite with WAL mode and FTS5 indexing.

SQLite is the source of truth during Phase 1. Embeddings may be added later as a secondary retrieval index, but they must not replace inspectable records or become a cloud dependency.

## Memory classes

### Working

Current task state, active constraints, temporary tool results, and unresolved decisions.

- Default retention: session or task lifetime
- Retrieval: exact task identifier first
- Durable only when explicitly promoted

### Episodic

What happened during a prior interaction or action.

- Examples: a model test failed, a setting changed, or a file was created
- Store outcome, timestamp, source, and verification state
- Prefer summaries over full transcripts

### Semantic

Stable facts and relationships.

- Examples: Senti and Sentionce are the same person; the project repository is Neon-Cortex
- Distinguish user-stated facts from inference
- User corrections supersede older records

### Preference

Durable choices that affect future behavior.

- Examples: local-first operation, GitHub connector first, and direct practical answers
- Store scope so project-specific preferences do not become universal rules accidentally

### Procedure

Verified ways to accomplish recurring tasks.

- Include platform, version assumptions, source, last verification date, and failure notes
- Expire or review records when dependencies change

## Required fields

Every durable memory record must include:

- `id`
- `type`
- `scope`
- `content`
- `source_kind`
- `source_reference`
- `created_at`
- `updated_at`
- `confidence`
- `retention`
- `status`

Useful optional fields include tags, entities, last-accessed time, access count, expiration, superseded-by, and verification metadata.

## Write policy

A memory may be committed when it is:

- Explicitly requested by Senti
- A stable user-stated fact or preference with future value
- A verified project decision
- A reusable procedure confirmed by successful execution
- A concise event summary required for continuity

Do not commit:

- Guesses presented as facts
- Temporary remarks without clear future value
- Secrets, passwords, tokens, or unnecessary private data
- Internal reasoning or private runtime instructions
- Every line of a conversation
- Model-generated claims that were not verified

Agents may propose memory writes. Only the memory service commits them after validation and deduplication.

## Retrieval policy

Retrieval happens in stages:

1. Apply scope and type filters.
2. Search exact identifiers and pinned records.
3. Use FTS5 lexical ranking.
4. Apply recency, confidence, and user-correction weighting.
5. Deduplicate overlapping records.
6. Return a token-bounded memory packet with source metadata.

The coordinator decides what enters the model context. Retrieval should favor a few highly relevant memories over many loosely related records.

## Conflict handling

When memories disagree:

1. Explicit newer user statements beat older user statements.
2. Verified outcomes beat plans or assumptions.
3. Project-scoped rules beat global defaults inside that project.
4. Higher-confidence records beat inferred records.
5. Unresolved conflicts must be surfaced rather than silently blended.

Superseded memories remain auditable but are excluded from normal retrieval.

## User control

The UI must eventually support:

- Search
- Pin and unpin
- Edit
- Forget or delete
- View source and scope
- See why a memory was retrieved
- Export and backup

Senti must be able to inspect what Cinder believes he knows and correct inaccurate records.

## Performance target

Scoped Phase 1 retrieval must be measured and kept below the perceived chat latency budget on the target Windows machine. Do not label retrieval fast without benchmarks.
