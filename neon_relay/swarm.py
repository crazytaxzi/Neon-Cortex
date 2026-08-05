from __future__ import annotations

import concurrent.futures
import json
import time
from dataclasses import asdict
from typing import Iterable

from .config import RelayConfig
from .contracts import JobContract, JobResult, WorkerReply, WorkerSpec
from .model_client import OpenAICompatibleClient
from .policy import validate_job
from .workspace import Workspace


PLANNER_SYSTEM = """You are one narrow planning worker inside Neon Relay. Produce compact JSON only. Analyze the goal and repository context. Return: {\"steps\":[...],\"files\":[...],\"risks\":[...],\"tests\":[...]}. Never claim execution."""

CODER_SYSTEM = """You are a coding worker. Return one complete unified git diff and nothing else. Keep changes minimal, preserve existing behavior, do not touch files outside the repository, and do not invent test results."""

CRITIC_SYSTEM = """You are the swarm critic. Compare candidate outputs for correctness, scope, safety, and likelihood of passing the stated tests. Return JSON only: {\"winner\":0,\"reason\":\"...\",\"fatal\":false}. winner is a zero-based candidate index."""

REPAIR_SYSTEM = """You repair a failed patch. Return one complete unified git diff and nothing else. Use the failure evidence and current repository snapshot. Fix the smallest real cause; do not claim tests passed."""

HEAVY_SYSTEM = """You are an escalation reviewer, not the master. Resolve a disagreement or repeated failure. Return JSON only with keys decision, diagnosis, next_action, and stop."""


class SwarmSupervisor:
    def __init__(self, config: RelayConfig, client: OpenAICompatibleClient | None = None):
        self.config = config
        self.client = client or OpenAICompatibleClient()

    def _parallel(self, workers: Iterable[WorkerSpec], messages: list[dict[str, str]]) -> list[WorkerReply]:
        specs = list(workers)
        if not specs:
            return []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(specs)) as pool:
            futures = [pool.submit(self.client.complete, worker, messages) for worker in specs]
            return [future.result() for future in futures]

    @staticmethod
    def _valid(replies: Iterable[WorkerReply]) -> list[WorkerReply]:
        return [reply for reply in replies if not reply.error and reply.text.strip()]

    def _choose(self, candidates: list[WorkerReply], goal: str, kind: str) -> tuple[int, str]:
        if len(candidates) == 1:
            return 0, "only valid candidate"
        critics = self.config.by_role("critic")
        payload = "\n\n".join(f"CANDIDATE {i}:\n{reply.text}" for i, reply in enumerate(candidates))
        replies = self._parallel(
            critics,
            [
                {"role": "system", "content": CRITIC_SYSTEM},
                {"role": "user", "content": f"Goal: {goal}\nCandidate type: {kind}\n{payload}"},
            ],
        )
        for reply in self._valid(replies):
            try:
                data = json.loads(self._json_only(reply.text))
                winner = int(data["winner"])
                if 0 <= winner < len(candidates):
                    return winner, str(data.get("reason", "critic selected candidate"))
            except (ValueError, KeyError, json.JSONDecodeError):
                continue
        winner = min(range(len(candidates)), key=lambda index: len(candidates[index].text))
        return winner, "deterministic shortest-valid fallback"

    @staticmethod
    def _json_only(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        start, end = text.find("{"), text.rfind("}")
        return text[start:end + 1] if start >= 0 and end >= start else text

    def _escalate(self, job: JobContract, evidence: str) -> str:
        if not job.heavy_escalation:
            return "heavy escalation disabled"
        workers = self.config.by_role(self.config.heavy_role)
        replies = self._parallel(
            workers,
            [
                {"role": "system", "content": HEAVY_SYSTEM},
                {"role": "user", "content": f"Goal: {job.goal}\nEvidence:\n{evidence[-12000:]}"},
            ],
        )
        valid = self._valid(replies)
        return valid[0].text if valid else "heavy reviewer unavailable"

    def run(self, job: JobContract) -> JobResult:
        started = time.monotonic()
        validate_job(job)
        workspace = Workspace(job.workspace, self.config.max_snapshot_bytes, self.config.max_file_bytes)
        workspace.ensure_clean()
        branch = workspace.create_branch(job.task_id)
        snapshot = workspace.snapshot(job)

        planners = self._parallel(
            self.config.by_role("planner"),
            [
                {"role": "system", "content": PLANNER_SYSTEM},
                {"role": "user", "content": f"TASK: {job.goal}\nTEST COMMANDS: {job.test_commands}\nREPOSITORY:\n{snapshot}"},
            ],
        )
        valid_plans = self._valid(planners)
        if not valid_plans:
            return JobResult(job.task_id, "blocked", branch=branch, summary="all planner workers failed")
        plan_index, plan_reason = self._choose(valid_plans, job.goal, "plan")
        plan = valid_plans[plan_index].text

        failures: list[dict[str, object]] = []
        for round_number in range(1, job.max_rounds + 1):
            if time.monotonic() - started > job.max_minutes * 60:
                return JobResult(job.task_id, "budget-exhausted", branch=branch, rounds=round_number - 1, summary="time budget exhausted", evidence={"failures": failures})

            current_snapshot = workspace.snapshot(job)
            role = "coder" if round_number == 1 else "repair"
            system = CODER_SYSTEM if round_number == 1 else REPAIR_SYSTEM
            failure_text = ""
            if failures:
                failure_text = "\nFAILURE EVIDENCE:\n" + json.dumps(failures[-1], indent=2)[-12000:]
            candidates = self._parallel(
                self.config.by_role(role) or self.config.by_role("coder"),
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"GOAL: {job.goal}\nPLAN:\n{plan}{failure_text}\nCURRENT REPOSITORY:\n{current_snapshot}"},
                ],
            )
            valid_candidates = self._valid(candidates)
            if not valid_candidates:
                escalation = self._escalate(job, json.dumps(failures))
                return JobResult(job.task_id, "blocked", branch=branch, rounds=round_number, summary="all coding workers failed", evidence={"escalation": escalation, "failures": failures})

            winner, patch_reason = self._choose(valid_candidates, job.goal, "patch")
            try:
                workspace.apply_patch(valid_candidates[winner].text)
            except RuntimeError as exc:
                failures.append({"round": round_number, "stage": "apply", "error": str(exc), "critic_reason": patch_reason})
                continue

            test_results = []
            passed = True
            for command in job.test_commands:
                result = workspace.run(command, timeout=min(job.max_minutes * 60, 900))
                test_results.append(asdict(result))
                if result.exit_code != 0:
                    passed = False
                    break

            if passed:
                commit = workspace.commit(job.task_id, job.goal) if job.allow_commit else None
                if job.allow_push:
                    push = workspace.git("push", "-u", "origin", branch, timeout=600)
                    if push.exit_code != 0:
                        return JobResult(job.task_id, "push-failed", branch=branch, commit=commit, rounds=round_number, summary=push.stderr, evidence={"tests": test_results})
                return JobResult(
                    job.task_id,
                    "completed",
                    branch=branch,
                    commit=commit,
                    rounds=round_number,
                    summary=f"completed; plan chosen because {plan_reason}; patch chosen because {patch_reason}",
                    evidence={"tests": test_results, "planner_workers": [asdict(x) for x in planners]},
                )

            failures.append({"round": round_number, "stage": "test", "tests": test_results, "critic_reason": patch_reason})
            workspace.git("reset", "--hard", "HEAD")

        escalation = self._escalate(job, json.dumps(failures))
        return JobResult(job.task_id, "failed", branch=branch, rounds=job.max_rounds, summary="retry budget exhausted", evidence={"failures": failures, "escalation": escalation})
