#!/usr/bin/env python3
"""CDP browser helper for crypto-agent."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError


def _get(path: str) -> Any:
    req = Request(path)
    with urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def post(path: str, payload: Dict[str, Any]) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = Request(path, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def ws_url() -> Optional[str]:
    try:
        version = _get("http://127.0.0.1:9222/json/version")
        return version.get("webSocketDebuggerUrl")
    except Exception:
        return None


def active_pages() -> List[Dict[str, Any]]:
    try:
        return _get("http://127.0.0.1:9222/json/list?active=1")
    except Exception:
        return []


def activate_tab(page_id: str) -> None:
    # Best-effort: ensure Chrome brings the page to front via activateTab equivalent.
    try:
        target = f"http://127.0.0.1:9222/json/activate/{page_id}"
        _get(target)
    except Exception:
        pass


def find_perplexity_tab() -> Optional[Dict[str, Any]]:
    for p in active_pages():
        if "perplexity.ai" in p.get("url", ""):
            return p
    return None


def navigate(url: str, page_id: str) -> None:
    target = f"http://127.0.0.1:9222/json/{page_id}"
    post(target, {"id": 1, "method": "Page.navigate", "params": {"url": url}})


def evaluate(expression: str, page_id: str) -> Any:
    target = f"http://127.0.0.1:9222/json/{page_id}"
    payload = {
        "id": 2,
        "method": "Runtime.evaluate",
        "params": {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        },
    }
    res = post(target, payload)
    result = res.get("result", {}).get("result", {})
    return result.get("value")
