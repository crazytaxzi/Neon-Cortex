from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WorkerSpec:
    name: str
    role: str
    endpoint: str
    model: str
    temperature: float = 0.2
    max_tokens: int = 768
    timeout_seconds: int = 180

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkerSpec":
        required = ("name", "role", "endpoint", "model")
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise ValueError(f"worker is missing required fields: {', '.join(missing)}")
        return cls(
            name=str(data["name"]),
            role=str(data["role"]),
            endpoint=str(data["endpoint"]).rstrip("/"),
            model=str(data["model"]),
            temperature=float(data.get("temperature", 0.2)),
            max_tokens=int(data.get("max_tokens", 768)),
            timeout_seconds=int(data.get("timeout_seconds", 180)),
        )


@dataclass(frozen=True)
class JobContract:
    task_id: str
    goal: str
    workspace: Path
    test_commands: tuple[tuple[str, ...], ...] = ()
    allowed_binaries: tuple[str, ...] = ("python", "py", "pytest", "git")
    max_rounds: int = 3
    max_minutes: int = 30
    allow_commit: bool = True
    allow_push: bool = False
    heavy_escalation: bool = True
    context_files: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JobContract":
        required = ("task_id", "goal", "workspace")
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise ValueError(f"job is missing required fields: {', '.join(missing)}")

        tests: list[tuple[str, ...]] = []
        for command in data.get("test_commands", []):
            if not isinstance(command, list) or not command:
                raise ValueError("each test command must be a non-empty JSON array")
            tests.append(tuple(str(part) for part in command))

        workspace_value = os.path.expandvars(str(data["workspace"]))
        return cls(
            task_id=str(data["task_id"]),
            goal=str(data["goal"]),
            workspace=Path(workspace_value).expanduser().resolve(),
            test_commands=tuple(tests),
            allowed_binaries=tuple(str(x).lower() for x in data.get("allowed_binaries", ["python", "py", "pytest", "git"])),
            max_rounds=max(1, int(data.get("max_rounds", 3))),
            max_minutes=max(1, int(data.get("max_minutes", 30))),
            allow_commit=bool(data.get("allow_commit", True)),
            allow_push=bool(data.get("allow_push", False)),
            heavy_escalation=bool(data.get("heavy_escalation", True)),
            context_files=tuple(str(x) for x in data.get("context_files", [])),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class WorkerReply:
    worker: str
    role: str
    text: str
    elapsed_seconds: float
    error: str | None = None


@dataclass
class CommandResult:
    argv: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    elapsed_seconds: float


@dataclass
class JobResult:
    task_id: str
    status: str
    branch: str | None = None
    commit: str | None = None
    rounds: int = 0
    summary: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
