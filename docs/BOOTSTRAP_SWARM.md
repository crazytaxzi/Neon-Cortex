# Bootstrap Swarm v0.1

Neon Relay is a deterministic local supervisor. It does not require GPT-OSS to be the permanent master and it does not require an OpenAI API key.

## Control hierarchy

1. Senti or ChatGPT creates a GitHub issue titled `[NEON TASK] ...` containing a JSON job contract.
2. Neon Relay claims the issue and owns the execution loop locally.
3. Two planner contexts work in parallel.
4. A critic context selects the tighter plan.
5. Two coding contexts produce competing unified diffs.
6. The critic selects one; deterministic code validates and applies it.
7. Relay runs allowlisted tests with `shell=False`.
8. Failed tests are returned to a repair worker for bounded retries.
9. GPT-OSS is only an optional escalation reviewer after disagreement or repeated failure.
10. A passing change is committed on `relay/<task-id>` and evidence is posted to the issue.

The scheduler, policy enforcement, branch handling, command execution, retry budgets, and evidence capture are ordinary Python. No model gets to improvise those controls.

## Worker economy

A worker is a role and an isolated context, not necessarily a separate weight file. One small general model server can expose several parallel slots for planners and critics. One small coder server can expose two coding slots and one repair slot.

Initial permanent roster:

- General hive: Qwen3.5-0.8B, four slots — two planners, critic, verifier.
- Coding hive: Qwen2.5-Coder-1.5B-Instruct, three slots — two coders, repair hand.
- Vision worker: Qwen3.5-2B, loaded on demand.
- Ear: Qwen3-ASR-0.6B.
- Mouth floor: Qwen3-TTS-12Hz-0.6B-Base.
- Heavy escalation: GPT-OSS-20B, used only when the small swarm cannot settle a task.

During bootstrap, the already-installed Qwen3.5-9B server may temporarily fill the general and coding roles so the relay can build its own smaller worker services.

## GitHub issue body

```json
{
  "task_id": "NC-BOOT-001",
  "goal": "Implement one small, testable repository change.",
  "workspace": "C:/Projects/Neon-Cortex",
  "test_commands": [["python", "-m", "pytest", "-q"]],
  "allowed_binaries": ["python", "py", "pytest", "git"],
  "max_rounds": 3,
  "max_minutes": 20,
  "allow_commit": true,
  "allow_push": false,
  "heavy_escalation": true
}
```

## Bootstrap steps

1. Pull the branch containing Neon Relay into the local Neon-Cortex clone.
2. Run `scripts/Install-NeonRelay.ps1` once.
3. Supply a fine-grained GitHub token restricted to the Neon-Cortex repository.
4. Configure model endpoints in `%LOCALAPPDATA%\Neon_Cortex\config\swarm.json`.
5. Start `%LOCALAPPDATA%\Neon_Cortex\Start-NeonRelay.cmd`.
6. Create the first `[NEON TASK]` issue.

The relay then continues without ChatGPT messages between every planning, coding, testing, and repair step. ChatGPT can inspect the resulting branch and evidence when present; local execution does not depend on the chat remaining open.
