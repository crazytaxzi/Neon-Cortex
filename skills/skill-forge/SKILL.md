# Skill Forge

## Purpose
Create and validate reusable Neon Cortex skills using one canonical package format.

## Trigger
Use this skill when Senti asks to create, scaffold, review, repair, or validate a reusable skill.

## Inputs
- Skill name
- Short description
- Trigger conditions
- Expected inputs and outputs
- Safety or confirmation requirements
- Optional examples and tests

## Procedure
1. Inspect the repository for existing conventions before creating files.
2. Convert the requested name to a safe kebab-case slug.
3. Create the package under `skills/<slug>/`.
4. Write `SKILL.md`, `README.md`, and `manifest.json`.
5. Add meaningful examples and validation tests where the skill behavior permits them.
6. Run `python -m skillforge validate skills/<slug>`.
7. Run automated tests when an execution tool is available.
8. Report exactly what was created, what was tested, and what remains unverified.

## Outputs
A self-contained skill package with this layout:

```text
skills/<slug>/
  SKILL.md
  README.md
  manifest.json
  tests/
  examples/
```

## Safety
Do not overwrite an existing skill without explicit approval. Never claim tests ran when no execution tool was available. Do not include secrets in generated examples or manifests.

## Validation
- Required paths exist.
- `manifest.json` parses and contains required fields.
- Manifest slug matches the directory name.
- Manifest entrypoint exists.
- Tests pass when execution is available.
