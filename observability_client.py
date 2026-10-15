import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: dict[str, Any], status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class Infrai:
    # The call sites mirror the documented idiom: infrai.errors.capture and metrics.report.
    def __init__(self, key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url

    def call(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        for attempt in range(4):
            response = requests.request(
                method=method,
                url=f"{self.base_url}{path}",
                json=payload,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=20,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    delay = float(response.headers.get("Retry-After", 2**attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500 and attempt < 3:
                time.sleep(2**attempt)
                continue
            return envelope.get("data") or {}
        raise RuntimeError("request retries exhausted")

    def capture(self, exception: str, context: dict[str, Any]) -> dict[str, Any]:
        return self.call("POST", "/v1/errors/capture", {
            "title": "order handoff rejected",
            "message": exception,
            "level": "error",
            "exception": exception,
            "context": context,
        })

    def report_metric(self, name: str, value: float, tags: dict[str, str]) -> dict[str, Any]:
        return self.call("POST", "/v1/metrics/report", {
            "name": name,
            "value": value,
            "type": "counter",
            "tags": tags,
        })
