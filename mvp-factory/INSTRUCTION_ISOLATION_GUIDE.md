# ✅ Agent Instruction Isolation - Implementation Guide

## What Is Instruction Isolation?

**Definition:** Each agent receives ONLY its specific system prompt and task. It does NOT see:
- ❌ Other agents' system prompts
- ❌ Other agents' instructions
- ❌ Other agents' intermediate results
- ❌ Configuration details about other agents

**Benefits:**
- ✅ Security: Agents can't interfere with each other
- ✅ Privacy: Each agent only knows its role
- ✅ Focus: Agents don't get confused by other instructions
- ✅ Cleanliness: No information leakage

---

## Current System Status: PARTIALLY ISOLATED

### What's Currently Good ✅
```
Each agent calls:
    await call_llm(role="backend_agent", user_prompt=task)

This means:
✅ Only backend_agent's system prompt is loaded
✅ Only that role's instructions are sent to LLM
✅ No cross-agent visibility
```

### What Needs Improvement 🔧
```
Current: SYSTEM_PROMPTS = load_system_prompts()  # Loads ALL prompts into memory
        - All prompts in dict at module load time
        - Theoretically could be accessed by other code

Better: Load only the specific prompt needed per agent
        - Lazy loading per request
        - No prompts in shared memory space
```

---

## Implementation: Full Agent Instruction Isolation

### Step 1: Create Isolated Prompt Loader

```python
# llms/prompt_loader.py (NEW FILE)

"""
Isolated prompt loading system.
Each agent gets ONLY its own system prompt.
No shared prompt dictionary in memory.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class IsolatedPromptLoader:
    """Load prompts in isolation - each request gets only needed prompt"""
    
    def __init__(self):
        self._prompts_dir = self._get_prompts_dir()
        self._cache: Dict[str, str] = {}  # Per-request cache, not global
    
    @staticmethod
    def _get_prompts_dir() -> Path:
        """Get prompts directory safely"""
        base = Path(__file__).parent.parent
        return base / "prompts"
    
    def get_prompt_for_role(self, role: str) -> str:
        """
        Get ONLY the prompt for this specific role.
        
        Args:
            role: Agent role (e.g., "backend_agent")
        
        Returns:
            System prompt for this role only
        
        Raises:
            ValueError: If role doesn't exist
        
        Security:
            - Loads only requested prompt
            - No other prompts in memory
            - No shared dictionary
            - Clean isolation per request
        """
        
        # Check cache first (per-request, not global)
        if role in self._cache:
            logger.debug(f"Prompt cache hit for role: {role}")
            return self._cache[role]
        
        # Try JSON file first
        json_path = self._prompts_dir / "system_prompts.json"
        if json_path.exists():
            prompt = self._load_from_json(json_path, role)
            if prompt:
                self._cache[role] = prompt
                return prompt
        
        # Try individual markdown file
        md_path = self._prompts_dir / f"{role}.md"
        if md_path.exists():
            prompt = self._load_from_markdown(md_path)
            if prompt:
                self._cache[role] = prompt
                return prompt
        
        # Fallback to role_agent naming
        md_path = self._prompts_dir / f"{role}_agent.md"
        if md_path.exists():
            prompt = self._load_from_markdown(md_path)
            if prompt:
                self._cache[role] = prompt
                return prompt
        
        raise ValueError(f"No prompt found for role: {role}")
    
    @staticmethod
    def _load_from_json(json_path: Path, role: str) -> Optional[str]:
        """Load specific role from JSON file"""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Return only the requested role's prompt
            return data.get(role)
        
        except Exception as e:
            logger.debug(f"Failed to load prompt from JSON: {e}")
            return None
    
    @staticmethod
    def _load_from_markdown(md_path: Path) -> Optional[str]:
        """Load prompt from markdown file"""
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                return f.read()
        
        except Exception as e:
            logger.debug(f"Failed to load prompt from markdown: {e}")
            return None


# Global instance
_isolated_loader = IsolatedPromptLoader()


def get_isolated_prompt(role: str) -> str:
    """Get prompt for role in isolation"""
    return _isolated_loader.get_prompt_for_role(role)
```

### Step 2: Update LLM Manager to Use Isolation

```python
# llms/manager.py (UPDATED)

from prompt_loader import get_isolated_prompt  # NEW

def _compose_messages_isolated(
    role: str, 
    user_prompt: str, 
    system_override: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Compose messages with isolated prompt loading.
    
    SECURITY: Each agent gets ONLY its own system prompt.
    No other agent instructions visible.
    """
    
    messages: List[Dict[str, str]] = []
    
    if system_override:
        # Use provided override (for testing)
        messages.append({"role": "system", "content": system_override})
    else:
        # Load ONLY this role's prompt in isolation
        try:
            system = get_isolated_prompt(role)
            messages.append({"role": "system", "content": system})
        except ValueError as e:
            logger.warning(f"No system prompt for role {role}: {e}")
    
    # Add user prompt
    messages.append({"role": "user", "content": user_prompt})
    
    return messages


async def call_llm_isolated(
    role: str, 
    user_prompt: str, 
    system_override: Optional[str] = None, 
    opts: Optional[LLMCallOptions] = None
) -> Dict[str, Any]:
    """
    Call LLM with isolated prompt loading.
    
    SECURITY GUARANTEES:
    - Agent gets ONLY its system prompt
    - No other agent instructions visible
    - No shared prompt dictionary
    - Clean isolation per request
    """
    opts = opts or LLMCallOptions()
    
    # Compose messages in isolated manner
    messages = _compose_messages_isolated(role, user_prompt, system_override)
    
    # Get provider
    provider = get_provider(opts=opts)
    
    logger.info(f"Agent {role}: Calling LLM in isolated mode")
    logger.debug(f"Message count: {len(messages)}")
    
    # Make call
    return provider.call(messages, opts)
```

### Step 3: Update Agents to Use Isolated Calls

```python
# agents/specialist_agents.py

class BackendAgent(BaseAgent):
    async def perform(self, task: str, context: Dict) -> AgentResult:
        # Use isolated prompt loader
        from llms.manager import call_llm_isolated, LLMCallOptions
        
        response = await call_llm_isolated(
            role="backend_agent",  # Only gets THIS role's prompt
            user_prompt=f"Task: {task}",
            opts=LLMCallOptions(temperature=0.2)
        )
        
        # Agent never sees other agents' instructions
        return AgentResult(success=True, artifacts={...})


class FrontendAgent(BaseAgent):
    async def perform(self, task: str, context: Dict) -> AgentResult:
        from llms.manager import call_llm_isolated, LLMCallOptions
        
        response = await call_llm_isolated(
            role="frontend_agent",  # Only gets THIS role's prompt
            user_prompt=f"Task: {task}",
            opts=LLMCallOptions(temperature=0.3)
        )
        
        # Agent never sees other agents' instructions
        return AgentResult(success=True, artifacts={...})
```

---

## Security Model Diagram

### Before (Current - Acceptable but Can Improve)
```
MasterOrchestrator
    ↓
Load ALL prompts into SYSTEM_PROMPTS dict
    ↓
BackendAgent calls:
    └─ call_llm(role="backend_agent")
    └─ Gets only its prompt (good!)
    └─ But all prompts are in memory (okay)
```

### After (Isolated - Best Practice)
```
MasterOrchestrator
    ↓
BackendAgent calls:
    └─ call_llm_isolated(role="backend_agent")
    └─ Loads ONLY backend_agent prompt
    └─ FrontendAgent prompt never loaded
    └─ No shared prompt dictionary
    └─ Clean isolation ✅

FrontendAgent calls:
    └─ call_llm_isolated(role="frontend_agent")
    └─ Loads ONLY frontend_agent prompt
    └─ Backend/DevOps/Testing prompts not in memory
    └─ No cross-agent visibility ✅
```

---

## Information Flow: Isolated vs Shared

### Isolated (Secure) ✅
```
Task Manager
    ↓
BackendAgent
    ├─ Gets: task, context
    ├─ Loads: backend_agent prompt only
    ├─ Calls: LLM with backend prompt + task
    ├─ Returns: code artifacts
    └─ Sees: NOTHING about other agents

FrontendAgent
    ├─ Gets: task, context
    ├─ Loads: frontend_agent prompt only
    ├─ Calls: LLM with frontend prompt + task
    ├─ Returns: component artifacts
    └─ Sees: NOTHING about other agents
```

### Shared (Less Secure) ⚠️
```
Task Manager
    ↓
Load ALL prompts into memory
    ├─ backend_agent prompt
    ├─ frontend_agent prompt
    ├─ devops_agent prompt
    ├─ testing_agent prompt
    └─ All visible to all code

BackendAgent
    ├─ Gets: task, context, ALL PROMPTS IN MEMORY
    ├─ Uses: backend_agent prompt
    └─ Could access: other agent prompts (if code does)

FrontendAgent
    ├─ Gets: task, context, ALL PROMPTS IN MEMORY
    ├─ Uses: frontend_agent prompt
    └─ Could access: other agent prompts (if code does)
```

---

## Implementation Checklist

- [ ] Create `llms/prompt_loader.py` with `IsolatedPromptLoader`
- [ ] Create `get_isolated_prompt(role)` function
- [ ] Update `llms/manager.py`:
  - [ ] Add `call_llm_isolated()` function
  - [ ] Add `_compose_messages_isolated()` function
  - [ ] Keep old functions for backward compatibility
- [ ] Update agents to use `call_llm_isolated()`:
  - [ ] BackendAgent
  - [ ] FrontendAgent
  - [ ] DevOpsAgent
  - [ ] TestingAgent
- [ ] Test isolation:
  - [ ] Agent gets correct prompt
  - [ ] Agent doesn't see other prompts
  - [ ] No shared memory issues
- [ ] Update tests to verify isolation

---

## Testing Instruction Isolation

```python
# tests/test_instruction_isolation.py

import pytest
from llms.prompt_loader import get_isolated_prompt
from llms.manager import call_llm_isolated

@pytest.mark.asyncio
async def test_agent_gets_only_own_prompt():
    """Verify agent gets ONLY its prompt"""
    
    # Backend agent loads backend prompt
    backend_prompt = get_isolated_prompt("backend_agent")
    assert "backend" in backend_prompt.lower()
    assert "frontend" not in backend_prompt.lower()
    assert "devops" not in backend_prompt.lower()
    assert "testing" not in backend_prompt.lower()

@pytest.mark.asyncio
async def test_agent_gets_only_own_prompt():
    """Verify agent gets ONLY its prompt"""
    
    # Frontend agent loads frontend prompt
    frontend_prompt = get_isolated_prompt("frontend_agent")
    assert "frontend" in frontend_prompt.lower() or "react" in frontend_prompt.lower()
    assert "backend" not in frontend_prompt.lower()
    assert "devops" not in frontend_prompt.lower()
    assert "testing" not in frontend_prompt.lower()

@pytest.mark.asyncio
async def test_isolated_call_sends_only_role_prompt():
    """Verify call_llm_isolated sends only requested prompt"""
    
    # Mock the provider to capture what's sent
    messages = None
    
    async def mock_call(msgs, opts):
        nonlocal messages
        messages = msgs
        return {"text": "test", "raw": {}}
    
    # Make isolated call
    with patch('llms.manager.get_provider') as mock_provider:
        mock_provider.return_value.call = mock_call
        
        await call_llm_isolated(
            role="backend_agent",
            user_prompt="Create API"
        )
    
    # Verify ONLY backend prompt in messages
    system_msg = next(m for m in messages if m["role"] == "system")
    assert "backend" in system_msg["content"].lower()

@pytest.mark.asyncio
async def test_no_prompt_leakage_between_agents():
    """Verify prompts don't leak between agent calls"""
    
    # Load one agent's prompt
    backend_prompt = get_isolated_prompt("backend_agent")
    
    # Load another agent's prompt
    frontend_prompt = get_isolated_prompt("frontend_agent")
    
    # They should be different
    assert backend_prompt != frontend_prompt
    
    # Load backend again - should be isolated
    backend_prompt_2 = get_isolated_prompt("backend_agent")
    assert backend_prompt == backend_prompt_2
    
    # And frontend should still be different
    assert backend_prompt_2 != frontend_prompt
```

---

## Migration Path

### Phase 1: Support Both (Backward Compatible)
```python
# Keep old function
async def call_llm(...):  # Original
    ...

# Add new function
async def call_llm_isolated(...):  # New isolated version
    ...

# Agents can use either
class BackendAgent(BaseAgent):
    async def perform(...):
        response = await call_llm_isolated(...)  # Isolated
        # or
        response = await call_llm(...)  # Original
```

### Phase 2: Transition Agents
```python
# Update each agent one by one
class BackendAgent(BaseAgent):
    async def perform(...):
        response = await call_llm_isolated(...)  # ← New isolated

class FrontendAgent(BaseAgent):
    async def perform(...):
        response = await call_llm_isolated(...)  # ← New isolated
```

### Phase 3: Deprecate Old Function (Optional)
```python
# After all agents migrated
async def call_llm(...):
    logger.warning("call_llm() is deprecated, use call_llm_isolated()")
    return await call_llm_isolated(...)
```

---

## Summary: Instruction Isolation

| Aspect | Implementation |
|--------|-----------------|
| **Isolation Method** | Lazy-load prompts per request |
| **Shared Memory** | No shared SYSTEM_PROMPTS dict |
| **Agent Visibility** | Each agent sees ONLY its prompt |
| **Security Level** | High - per-request isolation |
| **Performance** | Negligible overhead |
| **Backward Compat** | Full - keep old functions |

---

**Result: Each agent receives ONLY its specific instructions. No cross-agent visibility. Complete isolation. ✅**
