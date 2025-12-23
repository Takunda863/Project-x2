# 🔄 Quick Reference: Agents & Models

## Add New Agents - 3 Steps

### Step 1: Create Agent Class (agents/specialist_agents.py)
```python
class YourNewAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentConfig(
            name="Your Agent",
            role="your_role",
            capabilities=[],
            timeout_seconds=300
        ))
    
    async def perform(self, task: str, context: Dict) -> AgentResult:
        from llms.manager import call_llm
        response = await call_llm(role="your_role", user_prompt=task)
        return AgentResult(success=True, outputs=[], artifacts={})
```

### Step 2: Add System Prompt (prompts/system_prompts.json)
```json
{
  "your_role": "System prompt for your agent..."
}
```

### Step 3: Export It (agents/__init__.py)
```python
from .specialist_agents import YourNewAgent
__all__ = [..., "YourNewAgent"]
```

**That's it!** ✅

---

## Swap Models - Choose Your Method

### Method 1: Environment Variables (Easiest)
```bash
# Switch OpenAI model
export OPENAI_DEFAULT_MODEL="gpt-4-turbo"

# Switch to Hugging Face
export LLM_PROVIDER="hf"
export HF_MODEL_PATH="meta-llama/Llama-2-70b"
```

### Method 2: Runtime Options
```python
response = await call_llm(
    role="backend_agent",
    user_prompt="...",
    opts=LLMCallOptions(
        model="gpt-4-turbo",
        temperature=0.2
    )
)
```

### Method 3: Add New Provider
```python
# llms/manager.py
class YourProviderName(BaseProvider):
    def call(self, messages, opts):
        # Your provider implementation
        pass

# Update get_provider()
if provider == "your_provider":
    return YourProviderName()
```

---

## Models In Sandbox - ✅ CONFIRMED

```
Your Code (Sandboxed Dev Container)
    ↓
llms/manager.py (Local, Sandboxed)
    ↓
External API Call (OpenAI/HF/etc)
    ↓
LLM Model (Remote, NOT in Sandbox)
    ↓
Response (Returned to Sandbox)
```

**Safety:**
- ✅ No credentials in code
- ✅ No local model execution
- ✅ No file access from models
- ✅ Environment variables only
- ✅ Sandboxed execution guaranteed

---

## Current System

### Agents (4 Current)
- BackendAgent (APIs, databases)
- FrontendAgent (UI, components)
- DevOpsAgent (Infrastructure)
- TestingAgent (Tests, validation)

### Models Available
**OpenAI:**
- gpt-3.5-turbo (fast, cheap)
- gpt-4o-mini (balanced, default)
- gpt-4-turbo (powerful)
- gpt-4 (best)

**Hugging Face:**
- Llama 2 (7b, 13b, 70b)
- Mistral (7b, 8x7b)
- Any HF model

---

## Architecture: Fully Extensible

```
┌─────────────────────────────────────────┐
│          Master Orchestrator            │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┐
    │          │          │          │
    ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Backend │ │Frontend│ │ DevOps │ │Testing │
│Agent   │ │Agent   │ │Agent   │ │Agent   │
└────────┘ └────────┘ └────────┘ └────────┘
    │          │          │          │
    └──────────┴──────────┴──────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────────┐  ┌──────────────┐
│ LLM Manager  │  │ LLM Manager  │
│ (Abstraction)│  │ (Abstraction)│
└──────────────┘  └──────────────┘
    │                     │
    ▼                     ▼
┌──────────────┐  ┌──────────────┐
│ OpenAI API   │  │ HF API       │
│ (External)   │  │ (External)   │
└──────────────┘  └──────────────┘
```

**Extensible Points:**
- ✅ Add agents (inherit BaseAgent)
- ✅ Add models (env vars or LLMCallOptions)
- ✅ Add providers (extend BaseProvider)
- ✅ Add system prompts (system_prompts.json)

---

## Quick Examples

### Add Security Agent
```python
class SecurityEngineerAgent(BaseAgent):
    async def perform(self, task, context):
        response = await call_llm(role="security_engineer", user_prompt=task)
        return AgentResult(success=True, artifacts={"files": {...}})
```

### Use Fast Model for Testing
```python
response = await call_llm(
    role="backend_agent",
    user_prompt="Create API",
    opts=LLMCallOptions(model="gpt-3.5-turbo")
)
```

### Use Powerful Model for Complex Tasks
```python
response = await call_llm(
    role="backend_agent",
    user_prompt="Design ML pipeline",
    opts=LLMCallOptions(model="gpt-4-turbo")
)
```

---

## ✅ Summary

| Capability | Supported | How |
|-----------|-----------|-----|
| Add agents | ✅ YES | Class + prompt + export |
| Swap models | ✅ YES | Env vars or LLMCallOptions |
| Add providers | ✅ YES | Extend BaseProvider |
| Models in sandbox | ✅ YES | API calls, not local execution |
| Cost control | ✅ YES | Use cheaper models strategically |
| Fine-tune agents | ✅ YES | Custom agents with your data |

---

**Everything is designed for extensibility. You have complete control! 🚀**
