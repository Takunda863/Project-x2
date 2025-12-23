"""Role-aware LLM manager and provider adapters.

This module provides a small abstraction that composes per-role system
prompts with user prompts and routes calls to a provider adapter (OpenAI
or Hugging Face). It is intentionally minimal and does not require
credentials at import time; callers must set env vars and install the
provider SDKs to perform actual requests.

Usage examples and fallback behavior are documented in the functions.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _prompts_dir() -> str:
	"""Determine prompts directory relative to this file."""
	import os
	base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
	return os.path.join(base, "prompts")


def load_system_prompts() -> Dict[str, str]:
	"""Load system prompts from `prompts/system_prompts.json` if present,
	otherwise scan `prompts/*.md` for role-specific prompts (filename -> role).
	Returns a mapping role_name -> system_prompt.
	"""
	prompts_path = os.path.join(_prompts_dir(), "system_prompts.json")
	if os.path.exists(prompts_path):
		try:
			with open(prompts_path, "r", encoding="utf-8") as fh:
				return json.load(fh)
		except Exception:
			logger.exception("Failed to read system_prompts.json")

	# Fallback: read agent markdown prompts in the prompts directory
	prompts: Dict[str, str] = {}
	try:
		for name in os.listdir(_prompts_dir()):
			if not name.endswith(".md"):
				continue
			key = name.rsplit(".", 1)[0]
			with open(os.path.join(_prompts_dir(), name), "r", encoding="utf-8") as fh:
				prompts[key] = fh.read()
	except Exception:
		logger.debug("No prompts directory available or failed to read files")

	return prompts


SYSTEM_PROMPTS = load_system_prompts()


@dataclass
class LLMCallOptions:
	model: Optional[str] = None
	temperature: float = 0.2
	max_tokens: Optional[int] = None
	provider: Optional[str] = None  # 'openai' | 'hf' | None


def _compose_messages(role: str, user_prompt: str, system_override: Optional[str] = None) -> List[Dict[str, str]]:
	system = system_override or SYSTEM_PROMPTS.get(role) or SYSTEM_PROMPTS.get(f"{role}_agent")
	messages: List[Dict[str, str]] = []
	if system:
		messages.append({"role": "system", "content": system})
	messages.append({"role": "user", "content": user_prompt})
	return messages


class ProviderError(RuntimeError):
	pass


class BaseProvider:
	def call(self, messages: List[Dict[str, str]], opts: LLMCallOptions) -> Dict[str, Any]:
		raise NotImplementedError()


class OpenAIProvider(BaseProvider):
	def __init__(self, api_key: Optional[str] = None) -> None:
		self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
		if not self.api_key:
			raise ProviderError("OPENAI_API_KEY not set")

		try:
			import openai
		except Exception as exc:  # pragma: no cover - optional runtime dependency
			raise ProviderError("openai package not installed") from exc

		openai.api_key = self.api_key
		self._client = openai

	def call(self, messages: List[Dict[str, str]], opts: LLMCallOptions) -> Dict[str, Any]:
		params: Dict[str, Any] = {
			"model": opts.model or os.environ.get("OPENAI_DEFAULT_MODEL", "gpt-4o-mini") ,
			"messages": messages,
			"temperature": opts.temperature,
		}
		if opts.max_tokens:
			params["max_tokens"] = opts.max_tokens

		resp = self._client.ChatCompletion.create(**params)
		text = resp["choices"][0]["message"]["content"]
		return {"text": text, "raw": resp}


class HFProvider(BaseProvider):
	def __init__(self, model: Optional[str] = None) -> None:
		try:
			from transformers import pipeline  # type: ignore
		except Exception as exc:  # pragma: no cover - optional runtime dependency
			raise ProviderError("transformers package not installed") from exc

		self.model = model or os.environ.get("HF_MODEL_PATH")
		if not self.model:
			raise ProviderError("HF_MODEL_PATH not set and no model provided")

		self._pipe = pipeline("text-generation", model=self.model)

	def call(self, messages: List[Dict[str, str]], opts: LLMCallOptions) -> Dict[str, Any]:
		prompt = "\n\n".join([m["content"] for m in messages])
		out = self._pipe(prompt, max_length=opts.max_tokens or 512, temperature=opts.temperature)
		text = out[0]["generated_text"]
		return {"text": text, "raw": out}


def get_provider(preferred: Optional[str] = None, opts: Optional[LLMCallOptions] = None) -> BaseProvider:
	opts = opts or LLMCallOptions()
	provider = preferred or opts.provider or os.environ.get("LLM_PROVIDER")
	if provider == "hf":
		return HFProvider(model=opts.model)
	# default to OpenAI if available
	return OpenAIProvider()


def call_llm(role: str, user_prompt: str, system_override: Optional[str] = None, opts: Optional[LLMCallOptions] = None) -> Dict[str, Any]:
	"""Compose system+user messages for `role` and call the selected provider.

	Returns a dict containing `text` and `raw` provider response. This function
	will raise `ProviderError` if no provider can be initialized.
	"""
	opts = opts or LLMCallOptions()
	messages = _compose_messages(role, user_prompt, system_override=system_override)
	provider = get_provider(opts=opts)
	logger.debug("Calling provider %s for role %s", provider.__class__.__name__, role)
	return provider.call(messages, opts)


__all__ = ["LLMCallOptions", "call_llm", "ProviderError", "OpenAIProvider", "HFProvider"]

