from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class RunHub:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, run_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[run_id].add(ws)

    def disconnect(self, run_id: int, ws: WebSocket) -> None:
        self._connections[run_id].discard(ws)

    async def broadcast(self, run_id: int, event: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._connections[run_id]):
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(run_id, ws)


run_hub = RunHub()


class ManualGateStore:
    def __init__(self) -> None:
        self._events: dict[tuple[int, str], asyncio.Event] = {}
        self._decision: dict[tuple[int, str], bool] = {}

    def wait_event(self, run_id: int, action_type: str) -> asyncio.Event:
        key = (run_id, action_type)
        self._events.setdefault(key, asyncio.Event())
        return self._events[key]

    def resolve(self, run_id: int, action_type: str, approved: bool) -> None:
        key = (run_id, action_type)
        self._decision[key] = approved
        self.wait_event(run_id, action_type).set()

    def get_decision(self, run_id: int, action_type: str) -> bool:
        return self._decision.get((run_id, action_type), False)


manual_gates = ManualGateStore()
