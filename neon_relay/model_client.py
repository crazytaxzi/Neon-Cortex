from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Iterable

from .contracts import WorkerReply, WorkerSpec


class OpenAICompatibleClient:
    def complete(self, worker: WorkerSpec, messages: Iterable[dict[str, str]]) -> WorkerReply:
        payload = {
            "model": worker.model,
            "messages": list(messages),
            "temperature": worker.temperature,
            "max_tokens": worker.max_tokens,
            "stream": False,
        }
        request = urllib.request.Request(
            f"{worker.endpoint}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=worker.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
            text = str(data["choices"][0]["message"]["content"])
            return WorkerReply(worker.name, worker.role, text, time.perf_counter() - started)
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as exc:
            return WorkerReply(worker.name, worker.role, "", time.perf_counter() - started, str(exc))
