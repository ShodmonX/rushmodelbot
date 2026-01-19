from __future__ import annotations

from typing import Any

import httpx


class NgrokError(RuntimeError):
    pass


def _extract_https_url(payload: dict[str, Any]) -> str | None:
    tunnels = payload.get("tunnels", [])
    for tunnel in tunnels:
        public_url = tunnel.get("public_url")
        if isinstance(public_url, str) and public_url.startswith("https://"):
            return public_url
    return None


async def fetch_public_ngrok_url(base_url: str = "http://ngrok:4040") -> str:
    url = f"{base_url}/api/tunnels"
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    https_url = _extract_https_url(data)
    if not https_url:
        raise NgrokError("HTTPS tunnel not found in ngrok response")
    return https_url
