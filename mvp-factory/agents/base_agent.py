"""Base agent API for MVP Factory.

Provides a small, well-typed `BaseAgent` class and supporting types that
other specialist agents can extend. Keep this file lightweight — concrete
LLM integrations and agent implementations should live in separate modules.

Usage:
	class BackendAgent(BaseAgent):
		async def perform(self, task: str, context: dict) -> AgentResult:
			# implement
			...

	agent = BackendAgent(AgentConfig(name="backend", role="Backend Engineer"))
	result = await agent.run("Create a FastAPI service", {})
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import asyncio
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
	name: str
	role: str
	capabilities: List[str] = field(default_factory=list)
	timeout_seconds: Optional[int] = 300


@dataclass
class AgentResult:
	success: bool
	outputs: List[str] = field(default_factory=list)
	artifacts: Dict[str, Any] = field(default_factory=dict)
	error: Optional[str] = None


class BaseAgent(ABC):
	"""Abstract base class for all agents.

	Implementors should override `perform` with the agent's core behavior.
	The `run` method handles timeout, logging and basic error handling.
	"""

	def __init__(self, config: AgentConfig) -> None:
		self.config = config
		self._running = False

	async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
		"""Execute the agent on `task` with optional `context`.

		This wrapper enforces timeouts and captures exceptions into an
		`AgentResult` so callers can handle failures uniformly.
		"""
		context = context or {}
		timeout = self.config.timeout_seconds
		start = time.time()

		try:
			self._running = True
			if timeout:
				result = await asyncio.wait_for(self.perform(task, context), timeout=timeout)
			else:
				result = await self.perform(task, context)
			elapsed = time.time() - start
			logger.info("Agent %s finished task in %.2fs", self.config.name, elapsed)
			return result
		except asyncio.TimeoutError:
			msg = f"Agent {self.config.name} timed out after {timeout}s"
			logger.exception(msg)
			return AgentResult(success=False, error=msg)
		except Exception as exc:  # noqa: BLE001 - capture errors for structured result
			msg = f"Agent {self.config.name} failed: {exc}"
			logger.exception(msg)
			return AgentResult(success=False, error=msg)
		finally:
			self._running = False

	@abstractmethod
	async def perform(self, task: str, context: Dict[str, Any]) -> AgentResult:
		"""Core agent logic to implement.

		Should return an `AgentResult` describing success, outputs and any
		generated artifacts (files, snippets, manifests).
		"""

	def is_running(self) -> bool:
		return self._running

	# Small helpers that concrete agents can override or use
	async def stream_progress(self, message: str) -> None:
		"""Hook for streaming progress updates to an orchestrator or UI."""
		logger.debug("%s: %s", self.config.name, message)

	def summarize_result(self, result: AgentResult) -> str:
		"""Return a short one-line summary for the agent result."""
		if result.success:
			return f"{self.config.name}: success, outputs={len(result.outputs)}, artifacts={len(result.artifacts)}"
		return f"{self.config.name}: failed ({result.error})"


__all__ = ["AgentConfig", "AgentResult", "BaseAgent"]

