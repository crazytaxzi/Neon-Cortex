# Example: create a memory-audit skill

```powershell
python -m skillforge create "Memory Audit" --description "Checks durable memory records for missing metadata"
python -m skillforge validate skills/memory-audit
```

After scaffolding, replace every placeholder in `skills/memory-audit/SKILL.md`
and add tests that verify its deterministic validation behavior.
