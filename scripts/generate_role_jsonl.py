"""Generate JSONL fine-tune templates per role.

Creates files under `data/fine_tune_templates/{role}.jsonl` containing the
three-line JSONL template the project uses for hosted fine-tunes:

  {"role":"system","content":"<ROLE SYSTEM PROMPT>"}
  {"role":"user","content":"<TASK / USER PROMPT>"}
  {"role":"assistant","content":"<EXPECTED OUTPUT>"}

The script uses `prompts/system_prompts.json` as the canonical source of
system prompts and writes simple example tasks for each role. These are
templates — you should fill `assistant` with real expected outputs before
starting a fine-tune job.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


PROMPTS = Path(__file__).resolve().parents[1] / "prompts" / "system_prompts.json"
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "fine_tune_templates"


SAMPLE_TASKS: Dict[str, List[str]] = {
    "master_orchestrator": [
        "Given a product spec for a todo app, produce a master execution plan and task graph.",
        "Decompose 'real-time chat app' into parallel tasks for frontend, backend, and infra.",
    ],
    "github_coordinator": [
        "Create a repository skeleton for a FastAPI + Next.js project with branch strategy.",
    ],
    "ml_dl_engineer": [
        "Design a lightweight PyTorch training loop for a text classification model.",
    ],
    "backend_agent": [
        "Implement a REST endpoint /tasks with CRUD operations and SQLite persistence.",
    ],
    "ui_ux_engineer": [
        "Create a responsive tasks list component in Next.js with accessible markup.",
    ],
    "devops_engineer": [
        "Provide a Dockerfile and GitHub Actions workflow to build and push an image.",
    ],
    "cicd_integration": [
        "Define CI workflow steps to run lint, tests, build artifacts, and deploy to staging.",
    ],
    "testing_validation": [
        "Write pytest unit tests for the backend /tasks endpoints covering success and failure cases.",
    ],
}


def main() -> None:
    if not PROMPTS.exists():
        raise SystemExit("prompts/system_prompts.json missing — create it first.")
    out = OUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))
    for role, sys_text in prompts.items():
        examples = SAMPLE_TASKS.get(role, ["Describe a representative task for this role."])
        path = out / f"{role}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for t in examples:
                fh.write(json.dumps({"role": "system", "content": sys_text}, ensure_ascii=False) + "\n")
                fh.write(json.dumps({"role": "user", "content": t}, ensure_ascii=False) + "\n")
                fh.write(json.dumps({"role": "assistant", "content": "<EXPECTED_OUTPUT_PLACEHOLDER>"}, ensure_ascii=False) + "\n")
        print("Wrote", path)


if __name__ == "__main__":
    main()
