from __future__ import annotations

from pathlib import Path

from .contracts import JobContract


class PolicyError(RuntimeError):
    pass


def validate_job(job: JobContract) -> None:
    if not job.workspace.exists() or not job.workspace.is_dir():
        raise PolicyError(f"workspace does not exist: {job.workspace}")
    if not (job.workspace / ".git").exists():
        raise PolicyError(f"workspace is not a Git repository: {job.workspace}")
    if job.allow_push and not job.allow_commit:
        raise PolicyError("push cannot be enabled while commits are disabled")
    for command in job.test_commands:
        binary = Path(command[0]).name.lower()
        if binary.endswith(".exe"):
            binary = binary[:-4]
        if binary not in job.allowed_binaries:
            raise PolicyError(f"test command is not allowlisted: {command[0]}")
        forbidden = {"&", "&&", "|", "||", ";", ">", "<"}
        if any(part in forbidden for part in command):
            raise PolicyError("shell operators are forbidden; provide argv arrays")
