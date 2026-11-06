"""OpenAI 호환 Chat Completions 클라이언트 (표준 라이브러리만 사용).
FakeLLM은 테스트/드라이런용."""
import base64
import json
import re
import time
import urllib.request
import urllib.error
from typing import Any, Protocol

from .config import Endpoint


class LLM(Protocol):
    def chat(self, messages: list[dict], **kw: Any) -> str: ...


class OpenAICompatLLM:
    def __init__(self, ep: Endpoint, timeout: int = 300, retries: int = 3):
        self.ep, self.timeout, self.retries = ep, timeout, retries

    def chat(self, messages: list[dict], temperature: float = 0.0,
             json_mode: bool = False, max_tokens: int = 8192, **extra: Any) -> str:
        body: dict[str, Any] = {"model": self.ep.model, "messages": messages,
                                "temperature": temperature, "max_tokens": max_tokens, **extra}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        url = self.ep.base_url.rstrip("/") + "/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.ep.api_key:
            headers["Authorization"] = f"Bearer {self.ep.api_key}"
        last: Exception | None = None
        for i in range(self.retries):
            try:
                req = urllib.request.Request(url, json.dumps(body).encode(), headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    data = json.load(r)
                return data["choices"][0]["message"]["content"] or ""
            except (urllib.error.URLError, TimeoutError, KeyError) as e:
                last = e
                time.sleep(2 ** i)
        raise RuntimeError(f"LLM 호출 실패: {last}")


class FakeLLM:
    """responder(messages)->str. 호출 기록을 calls에 남긴다."""
    def __init__(self, responder):
        self.responder, self.calls = responder, []

    def chat(self, messages, **kw):
        self.calls.append((messages, kw))
        return self.responder(messages)


def image_message(prompt: str, png_bytes: bytes) -> list[dict]:
    b64 = base64.b64encode(png_bytes).decode()
    return [{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}]}]


def parse_json(text: str) -> Any:
    """모델 출력에서 JSON을 관대하게 꺼낸다 (```json 펜스, 앞뒤 잡설 허용)."""
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        s = min([i for i in (t.find("{"), t.find("[")) if i >= 0], default=-1)
        e = max(t.rfind("}"), t.rfind("]"))
        if s >= 0 and e > s:
            return json.loads(t[s:e + 1])
        raise
