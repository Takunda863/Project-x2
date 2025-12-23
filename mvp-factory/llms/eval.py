"""Small evaluation harness to compare base vs fine-tuned models.

This script attempts to call `call_llm` for a list of example prompts
and prints outputs. It will not run unless provider credentials and
optional SDKs are installed.
"""

from __future__ import annotations

import os
from mvp_factory.llms.manager import call_llm, LLMCallOptions, ProviderError


EXAMPLES = [
    "Write a small FastAPI endpoint that returns 'hello world'",
    "Design a PostgreSQL schema for a task manager app",
]


def run_examples(role: str = "backend_agent") -> None:
    opts = LLMCallOptions()
    for ex in EXAMPLES:
        try:
            resp = call_llm(role, ex, opts=opts)
            print("PROMPT:", ex)
            print("OUTPUT:\n", resp.get("text"))
            print("---\n")
        except ProviderError as e:
            print("Provider not available:", e)
            return


if __name__ == "__main__":
    run_examples()
