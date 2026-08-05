from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from neon_relay.config import RelayConfig
from neon_relay.contracts import JobContract, WorkerReply, WorkerSpec
from neon_relay.policy import PolicyError, validate_job
from neon_relay.swarm import SwarmSupervisor
from neon_relay.workspace import Workspace


class FakeClient:
    def __init__(self, replies: dict[str, str]):
        self.replies = replies

    def complete(self, worker: WorkerSpec, messages):
        return WorkerReply(worker.name, worker.role, self.replies.get(worker.name, ""), 0.01)


def test_config_groups_roles(tmp_path: Path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"workers": [
        {"name": "a", "role": "planner", "endpoint": "http://x", "model": "m"},
        {"name": "b", "role": "planner", "endpoint": "http://x", "model": "m"},
    ]}), encoding="utf-8")
    config = RelayConfig.load(path)
    assert [worker.name for worker in config.by_role("planner")] == ["a", "b"]


def test_policy_rejects_shell_operators(tmp_path: Path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    job = JobContract.from_dict({
        "task_id": "x", "goal": "x", "workspace": str(tmp_path),
        "test_commands": [["python", "-m", "pytest", "&&", "echo"]],
    })
    with pytest.raises(PolicyError):
        validate_job(job)


def test_extracts_fenced_diff():
    text = "before\n```diff\ndiff --git a/a.txt b/a.txt\n--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-a\n+b\n```\nafter"
    patch = Workspace._extract_patch(text)
    assert patch.startswith("diff --git")
    assert "after" not in patch


def test_critic_selects_candidate():
    workers = (WorkerSpec("critic", "critic", "http://x", "m"),)
    config = RelayConfig(workers=workers)
    client = FakeClient({"critic": '{"winner":1,"reason":"second is tighter","fatal":false}'})
    supervisor = SwarmSupervisor(config, client=client)
    candidates = [
        WorkerReply("a", "coder", "long candidate", 0.1),
        WorkerReply("b", "coder", "short", 0.1),
    ]
    winner, reason = supervisor._choose(candidates, "goal", "patch")
    assert winner == 1
    assert "tighter" in reason


def test_job_contract_requires_argv_arrays(tmp_path: Path):
    with pytest.raises(ValueError):
        JobContract.from_dict({
            "task_id": "x", "goal": "x", "workspace": str(tmp_path),
            "test_commands": ["pytest -q"],
        })
