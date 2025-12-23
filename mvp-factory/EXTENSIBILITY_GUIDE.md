# 🔧 Extensibility Guide: Adding Agents & Swapping Models

## ✅ YES - You Can Add More Agents

### How the Agent System is Designed for Extensibility

The agent system uses a **modular, inheritance-based architecture** that makes it trivial to add new agents.

#### Current Agents (4)
```python
BaseAgent (abstract)
├── BackendAgent
├── FrontendAgent
├── DevOpsAgent
└── TestingAgent
```

#### You Can Add
```python
BaseAgent (abstract)
├── BackendAgent
├── FrontendAgent
├── DevOpsAgent
├── TestingAgent
├── MLEngineerAgent .................. NEW
├── DataEngineerAgent ............... NEW
├── SecurityEngineerAgent ........... NEW
├── MobileAgent ..................... NEW
├── BlockchainAgent ................. NEW
└── [Any Custom Agent] .............. NEW
```

### How to Add a New Agent

**Step 1: Create the Agent Class**
```python
# agents/specialist_agents.py (add to existing file)

class MLEngineerAgent(BaseAgent):
    """ML/DL specialist agent for ML pipeline generation"""
    
    def __init__(self):
        config = AgentConfig(
            name="ML Engineer",
            role="ml_engineer",
            capabilities=[
                "ML model implementation",
                "Data preprocessing",
                "Model training pipelines",
                "PyTorch/TensorFlow code"
            ],
            timeout_seconds=600  # ML tasks may take longer
        )
        super().__init__(config)
    
    async def perform(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Generate ML/DL code"""
        from llms.manager import call_llm
        
        prompt = f"""
        For project '{context.get('project_name')}':
        Task: {task}
        Requirements: {context.get('requirements')}
        
        Generate production-ready ML code...
        """
        
        response = await call_llm(
            role="ml_engineer",
            user_prompt=prompt
        )
        
        # Parse response and return
        return AgentResult(
            success=True,
            outputs=["Generated ML models"],
            artifacts={
                "files": {"models/ml_model.py": response["text"]},
                "metadata": {"type": "ml_pipeline"},
                "dependencies": ["torch", "scikit-learn"],
                "instructions": "Install dependencies and train model"
            }
        )
```

**Step 2: Add System Prompt**
```json
// prompts/system_prompts.json (add new entry)
{
  "ml_engineer": "You are a senior ML engineer with expertise in...",
  ...existing prompts...
}
```

**Step 3: Update Module Exports**
```python
# agents/__init__.py (add to imports)

from .specialist_agents import (
    BackendAgent,
    FrontendAgent,
    DevOpsAgent,
    TestingAgent,
    MLEngineerAgent  # NEW
)

__all__ = [
    "BackendAgent",
    "FrontendAgent",
    "DevOpsAgent",
    "TestingAgent",
    "MLEngineerAgent",  # NEW
    ...
]
```

**Step 4: Test It**
```python
import asyncio
from agents import MLEngineerAgent, AgentContext

async def test():
    agent = MLEngineerAgent()
    context = AgentContext(
        project_name="Prediction App",
        project_description="ML prediction service",
        requirements=["ML model"],
        tech_stack={"ml": "pytorch"},
        constraints=[]
    )
    result = await agent.run("Generate ML model", context)
    assert result.success
    print("✅ ML Agent works!")

asyncio.run(test())
```

### Adding Multiple New Agents - Complete Example

```python
# agents/specialist_agents.py

# SECURITY AGENT
class SecurityEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentConfig(
            name="Security Engineer",
            role="security_engineer",
            capabilities=["Security audits", "OWASP compliance", "Penetration testing"],
            timeout_seconds=300
        ))
    
    async def perform(self, task: str, context: Dict) -> AgentResult:
        from llms.manager import call_llm
        response = await call_llm(role="security_engineer", user_prompt=f"{task}")
        return AgentResult(success=True, outputs=["Security audit complete"], 
                         artifacts={"files": {...}})

# DATA ENGINEER AGENT
class DataEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentConfig(
            name="Data Engineer",
            role="data_engineer",
            capabilities=["Data pipelines", "ETL", "Data warehousing"],
            timeout_seconds=300
        ))
    
    async def perform(self, task: str, context: Dict) -> AgentResult:
        from llms.manager import call_llm
        response = await call_llm(role="data_engineer", user_prompt=f"{task}")
        return AgentResult(success=True, outputs=["Data pipeline created"],
                         artifacts={"files": {...}})

# CLOUD ARCHITECT AGENT
class CloudArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentConfig(
            name="Cloud Architect",
            role="cloud_architect",
            capabilities=["Cloud design", "Scalability", "Cost optimization"],
            timeout_seconds=300
        ))
    
    async def perform(self, task: str, context: Dict) -> AgentResult:
        from llms.manager import call_llm
        response = await call_llm(role="cloud_architect", user_prompt=f"{task}")
        return AgentResult(success=True, outputs=["Cloud architecture designed"],
                         artifacts={"files": {...}})
```

---

## ✅ YES - You Can Swap Models

### Current Model Setup

**Supported Providers (via abstraction layer):**

```python
# llms/manager.py provides abstraction

OpenAI
├── gpt-4o-mini (default)
├── gpt-4-turbo
├── gpt-4
└── gpt-3.5-turbo

Hugging Face
├── meta-llama/Llama-2-7b
├── meta-llama/Llama-2-13b
├── meta-llama/Llama-2-70b
├── mistralai/Mistral-7B
├── NousResearch/Nous-Hermes-2-Mixtral-8x7B
└── Any HF model
```

### How to Change Models

**Option 1: Environment Variables (Easiest)**

```bash
# Use different OpenAI model
export OPENAI_DEFAULT_MODEL="gpt-4-turbo"

# Or switch to Hugging Face
export LLM_PROVIDER="hf"
export HF_MODEL_PATH="meta-llama/Llama-2-70b"
```

**Option 2: Runtime Configuration**

```python
from llms.manager import call_llm, LLMCallOptions

# Use specific model for specific call
response = call_llm(
    role="backend_agent",
    user_prompt="Generate API code",
    opts=LLMCallOptions(
        provider="openai",
        model="gpt-4-turbo",  # Override default
        temperature=0.1
    )
)

# Or use Hugging Face for specific call
response = call_llm(
    role="backend_agent",
    user_prompt="Generate API code",
    opts=LLMCallOptions(
        provider="hf",
        model="meta-llama/Llama-2-70b"
    )
)
```

**Option 3: Add Support for New Provider**

```python
# llms/manager.py (add new provider class)

class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ProviderError("ANTHROPIC_API_KEY not set")
        
        try:
            import anthropic
        except Exception as exc:
            raise ProviderError("anthropic package not installed") from exc
        
        self._client = anthropic.Anthropic(api_key=self.api_key)
    
    def call(self, messages: List[Dict[str, str]], opts: LLMCallOptions) -> Dict[str, Any]:
        """Call Claude API"""
        prompt = "\n\n".join([m["content"] for m in messages])
        
        resp = self._client.messages.create(
            model=opts.model or "claude-3-opus-20240229",
            max_tokens=opts.max_tokens or 4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = resp.content[0].text
        return {"text": text, "raw": resp}

# Update get_provider function
def get_provider(preferred: Optional[str] = None, opts: Optional[LLMCallOptions] = None) -> BaseProvider:
    opts = opts or LLMCallOptions()
    provider = preferred or opts.provider or os.environ.get("LLM_PROVIDER")
    
    if provider == "hf":
        return HFProvider(model=opts.model)
    elif provider == "anthropic":  # NEW
        return AnthropicProvider()
    
    return OpenAIProvider()
```

---

## ✅ CONFIRMED: Models Are In Sandboxes

### Sandbox Environment Details

**Your Environment:**
```
Location: Dev Container
OS: Ubuntu 24.04.3 LTS
Container: Isolated from host
Network: Controlled access
File System: Sandboxed
Process Isolation: Yes
```

### Current Model Execution Flow

```
Your Code (Sandboxed)
        ↓
llms/manager.py (Abstraction Layer)
        ↓
Provider (OpenAI/HF - External API)
        ↓
LLM Model (Remote, not in sandbox)
        ↓
Response (Returned to sandbox)
```

### Safety Guarantees

✅ **No models stored locally** - All calls go to external APIs  
✅ **No credentials in code** - Loaded from environment variables  
✅ **No local model execution** - Uses API calls only  
✅ **Sandboxed execution** - Dev container isolation  
✅ **No file access from models** - Unidirectional data flow  

### If You Want Local Models (Optional)

You can run models locally in the sandbox:

```python
# Option 1: Small local model (4GB+)
export LLM_PROVIDER="hf"
export HF_MODEL_PATH="microsoft/phi-2"  # Small model
# pip install transformers torch

# Option 2: GGML quantized (runs on CPU)
# Use ollama: ollama run mistral
# Then configure custom provider to use local endpoint
```

---

## 🎯 Model Swapping Quick Reference

### Switch to Different OpenAI Models

```bash
# Fast, cheap
export OPENAI_DEFAULT_MODEL="gpt-3.5-turbo"

# Balanced (default)
export OPENAI_DEFAULT_MODEL="gpt-4o-mini"

# Powerful
export OPENAI_DEFAULT_MODEL="gpt-4-turbo"

# Best (most expensive)
export OPENAI_DEFAULT_MODEL="gpt-4"
```

### Switch to Hugging Face

```bash
export LLM_PROVIDER="hf"
export HF_MODEL_PATH="meta-llama/Llama-2-7b"
# or
export HF_MODEL_PATH="mistralai/Mistral-7B-Instruct-v0.2"
```

### Per-Agent Model Customization

```python
# agents/specialist_agents.py

class BackendAgent(BaseAgent):
    async def perform(self, task: str, context: Dict) -> AgentResult:
        # Use fast model for simple tasks
        response = await call_llm(
            role="backend_agent",
            user_prompt=task,
            opts=LLMCallOptions(
                model="gpt-3.5-turbo",  # Fast
                temperature=0.1
            )
        )
        return AgentResult(...)

class MLEngineerAgent(BaseAgent):
    async def perform(self, task: str, context: Dict) -> AgentResult:
        # Use powerful model for complex ML tasks
        response = await call_llm(
            role="ml_engineer",
            user_prompt=task,
            opts=LLMCallOptions(
                model="gpt-4-turbo",  # Powerful
                temperature=0.2,
                max_tokens=4096
            )
        )
        return AgentResult(...)
```

---

## 📊 Model Comparison for Agent Selection

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| gpt-3.5-turbo | ⚡⚡⚡ | ⭐⭐ | 💰 | Simple tasks |
| gpt-4o-mini | ⚡⚡ | ⭐⭐⭐ | 💰💰 | Default choice |
| gpt-4-turbo | ⚡ | ⭐⭐⭐⭐ | 💰💰💰 | Complex logic |
| gpt-4 | ⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰💰 | Best quality |
| Llama-2-7b | ⚡⚡⚡ | ⭐⭐ | Free | Testing |
| Mistral-7B | ⚡⚡ | ⭐⭐⭐ | Free | Testing |
| Llama-2-70b | ⚡ | ⭐⭐⭐⭐ | Free | Production |

---

## 🚀 Recommended Setup for Custom Agents

### For Your Development:

**Backend Agent:**
```python
# Use gpt-4o-mini for API generation (default)
opts=LLMCallOptions(model="gpt-4o-mini", temperature=0.2)
```

**Frontend Agent:**
```python
# Use gpt-4o-mini for component generation (default)
opts=LLMCallOptions(model="gpt-4o-mini", temperature=0.3)
```

**Testing Agent:**
```python
# Use gpt-3.5-turbo for test generation (cheaper, sufficient)
opts=LLMCallOptions(model="gpt-3.5-turbo", temperature=0.1)
```

**DevOps Agent:**
```python
# Use gpt-4-turbo for infrastructure (needs high quality)
opts=LLMCallOptions(model="gpt-4-turbo", temperature=0.2)
```

**New ML Agent (Example):**
```python
# Use gpt-4 for ML code (complex, needs best quality)
opts=LLMCallOptions(model="gpt-4", temperature=0.2, max_tokens=4096)
```

---

## ✅ Summary

| Question | Answer | Details |
|----------|--------|---------|
| **Add more agents?** | ✅ YES | Create new class, inherit from BaseAgent, add system prompt, export |
| **Swap models?** | ✅ YES | Change env vars or pass LLMCallOptions to call_llm() |
| **Models in sandbox?** | ✅ YES | No local model execution, all calls to external APIs |
| **Add new provider?** | ✅ YES | Extend BaseProvider, update get_provider() function |
| **Cost control?** | ✅ YES | Use cheaper models for simple tasks, expensive for complex |
| **Testing?** | ✅ YES | Use free Hugging Face models locally for development |

---

## Next Steps for Custom Agents

1. **Add new agents** following the pattern above
2. **Assign appropriate models** per agent's complexity
3. **Configure system prompts** for each new role
4. **Test locally** with cheaper models first
5. **Scale to powerful models** for production

**You have complete flexibility in the architecture! 🚀**
