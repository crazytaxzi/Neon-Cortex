from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .contracts import JobContract, JobResult


_TASK_PREFIX = "[NEON TASK]"
_CLAIM_MARKER = "<!-- neon-relay:claimed -->"
_RESULT_MARKER = "<!-- neon-relay:result -->"


class GitHubBridge:
    def __init__(self, repository: str, token_file: Path):
        self.repository = repository
        self.token = token_file.read_text(encoding="utf-8").strip()
        if not self.token:
            raise ValueError("GitHub token file is empty")
        self.base = f"https://api.github.com/repos/{repository}"

    def _request(self, method: str, url: str, payload: dict[str, Any] | None = None) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Neon-Relay/0.1",
        }
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                return json.loads(body.decode("utf-8")) if body else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {exc.code}: {detail}") from exc

    def _comments(self, issue_number: int) -> list[dict[str, Any]]:
        return list(self._request("GET", f"{self.base}/issues/{issue_number}/comments?per_page=100"))

    def pending(self) -> list[tuple[int, JobContract]]:
        issues = self._request("GET", f"{self.base}/issues?state=open&per_page=100&sort=created&direction=asc")
        pending: list[tuple[int, JobContract]] = []
        for issue in issues:
            if "pull_request" in issue or not str(issue.get("title", "")).startswith(_TASK_PREFIX):
                continue
            comments = self._comments(int(issue["number"]))
            if any(_CLAIM_MARKER in str(comment.get("body", "")) for comment in comments):
                continue
            payload = self._extract_json(str(issue.get("body") or ""))
            pending.append((int(issue["number"]), JobContract.from_dict(payload)))
        return pending

    @staticmethod
    def _extract_json(body: str) -> dict[str, Any]:
        fenced = re.search(r"```json\s*(\{.*?\})\s*```", body, flags=re.DOTALL | re.IGNORECASE)
        text = fenced.group(1) if fenced else body.strip()
        return dict(json.loads(text))

    def claim(self, issue_number: int, task_id: str) -> None:
        self.comment(issue_number, f"{_CLAIM_MARKER}\nNeon Relay claimed `{task_id}` and started local execution.")

    def complete(self, issue_number: int, result: JobResult) -> None:
        body = f"{_RESULT_MARKER}\n```json\n{json.dumps(asdict(result), indent=2, default=str)}\n```"
        self.comment(issue_number, body)

    def comment(self, issue_number: int, body: str) -> None:
        self._request("POST", f"{self.base}/issues/{issue_number}/comments", {"body": body})
