from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List


class SessionService:
    """Very simple in-memory session store.

    This can be replaced with Redis for production envs.
    """

    def __init__(self) -> None:
        # {session_id: (timestamp, messages)}
        self._store: Dict[str, tuple[float, List[dict[str, Any]]]] = {}
        self._ttl_seconds = 60 * 60 * 24  # 24h
        # background cleanup
        asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self) -> None:  # pragma: no cover
        while True:
            await asyncio.sleep(3600)
            now = time.time()
            for k in list(self._store.keys()):
                ts, _ = self._store[k]
                if now - ts > self._ttl_seconds:
                    self._store.pop(k, None)

    def get_history(self, session_id: str) -> List[dict[str, Any]]:
        if session_id in self._store:
            ts, history = self._store[session_id]
            self._store[session_id] = (time.time(), history)
            return history
        return []

    def append_message(self, session_id: str, message: dict[str, Any]) -> None:
        if session_id in self._store:
            ts, history = self._store[session_id]
            history.append(message)
            self._store[session_id] = (time.time(), history)
        else:
            self._store[session_id] = (time.time(), [message])
