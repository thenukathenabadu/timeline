"""
Event-date extraction via Ollama + Llama 3.2:1b.

This is Layer 2 — only called when we need to extract the real-world
event date from article text. Falls back gracefully if Ollama is
unreachable (Docker dev environment vs. local Ollama install).
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone

import httpx
from dateutil import parser as dateutil_parser

from ai.base import ReasoningProvider
from config import settings

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """\
You are a date extraction assistant. Given a news article, return ONLY the date the event occurred (not the publication date) in ISO 8601 format (YYYY-MM-DD). If the event date is unknown or the same as the publication date, return null.

Article title: {title}
Article summary: {summary}
Publication date: {published_at}

Respond with only a JSON object: {{"event_date": "YYYY-MM-DD"}} or {{"event_date": null}}"""


class OllamaProvider(ReasoningProvider):
    """Calls local Ollama server for date extraction."""

    async def extract_event_date(
        self,
        title: str,
        summary: str,
        published_at: datetime,
    ) -> datetime | None:
        prompt = _PROMPT_TEMPLATE.format(
            title=title,
            summary=summary or "",
            published_at=published_at.date().isoformat(),
        )
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={
                        "model": settings.reasoning_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0, "num_predict": 50},
                    },
                )
                resp.raise_for_status()
                raw = resp.json().get("response", "")
                return self._parse_response(raw, published_at)
        except Exception as exc:
            logger.debug("Ollama unavailable (%s) — skipping date extraction", exc)
            return None

    @staticmethod
    def _parse_response(raw: str, published_at: datetime) -> datetime | None:
        # Find the first JSON object in the response
        match = re.search(r'\{[^}]+\}', raw)
        if not match:
            return None
        try:
            data = json.loads(match.group())
            date_str = data.get("event_date")
            if not date_str:
                return None
            dt = dateutil_parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None
