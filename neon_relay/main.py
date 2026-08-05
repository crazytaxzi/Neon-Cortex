from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict
from pathlib import Path

from .config import RelayConfig
from .contracts import JobContract, JobResult
from .github_bridge import GitHubBridge
from .swarm import SwarmSupervisor


LOG = logging.getLogger("neon-relay")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Neon Relay local swarm supervisor")
    parser.add_argument("--config", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run-job", help="run one local JSON job")
    run.add_argument("job", type=Path)
    sub.add_parser("watch-github", help="poll GitHub issues for [NEON TASK] jobs")
    sub.add_parser("check", help="validate configuration and list worker roles")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = _parser().parse_args(argv)
    config = RelayConfig.load(args.config)

    if args.command == "check":
        roles: dict[str, list[str]] = {}
        for worker in config.workers:
            roles.setdefault(worker.role, []).append(worker.name)
        print(json.dumps({"ok": True, "roles": roles, "repo": config.github_repo}, indent=2))
        return 0

    supervisor = SwarmSupervisor(config)
    if args.command == "run-job":
        job = JobContract.from_dict(json.loads(args.job.read_text(encoding="utf-8-sig")))
        result = supervisor.run(job)
        print(json.dumps(asdict(result), indent=2, default=str))
        return 0 if result.status == "completed" else 2

    if not config.github_token_file:
        raise SystemExit("github_token_file is required for watch-github")
    bridge = GitHubBridge(config.github_repo, config.github_token_file)
    LOG.info("watching %s every %ss", config.github_repo, config.poll_seconds)
    while True:
        try:
            for issue_number, job in bridge.pending():
                bridge.claim(issue_number, job.task_id)
                try:
                    result = supervisor.run(job)
                except Exception as exc:
                    LOG.exception("task %s failed", job.task_id)
                    result = JobResult(job.task_id, "relay-error", summary=str(exc))
                bridge.complete(issue_number, result)
        except Exception:
            LOG.exception("GitHub polling cycle failed")
        time.sleep(config.poll_seconds)


if __name__ == "__main__":
    sys.exit(main())
