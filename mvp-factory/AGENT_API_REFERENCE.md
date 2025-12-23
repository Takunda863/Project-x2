# MVP Factory - API Reference for Custom Agents

## Quick Reference

### 1. BaseAgent Class

**Location:** `agents/base_agent.py`

```python
class BaseAgent(ABC):
    """All custom agents must inherit from this."""
    
    async def run(
        self, 
        task: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """
        Public interface - handles timeouts and error wrapping.
        
        Args:
            task: Description of what to do
            context: AgentContext object with project info
            
        Returns:
            AgentResult with success status, outputs, and artifacts
            
        Raises:
            asyncio.TimeoutError: If execution exceeds timeout_seconds
        """
    
    @abstractmethod
    async def perform(
        self, 
        task: str, 
        context: Dict[str, Any]
    ) -> AgentResult:
        """
        Implement this in your custom agent.
        
        Args:
            task: Description of what to do
            context: AgentContext with project details
            
        Returns:
            AgentResult object
        """
```

---

### 2. Data Classes

#### AgentConfig
```python
@dataclass
class AgentConfig:
    name: str                          # e.g., "Backend Generator"
    role: str                          # e.g., "backend_agent"
    capabilities: List[str]            # Features it can do
    timeout_seconds: Optional[int] = 300  # Max execution time
```

#### AgentResult
```python
@dataclass
class AgentResult:
    success: bool                      # Was execution successful?
    outputs: List[str]                # Human-readable descriptions
    artifacts: Dict[str, Any]         # Generated code/files
    error: Optional[str] = None       # Error message if failed
```

**artifacts structure:**
```python
artifacts = {
    "files": {                        # Generated file paths & contents
        "src/auth.py": "code here...",
        "src/models.py": "code here..."
    },
    "metadata": {                     # Structured information
        "framework": "fastapi",
        "orm": "sqlalchemy",
        "auth_method": "jwt"
    },
    "dependencies": [                 # Required packages
        "fastapi>=0.95.0",
        "sqlalchemy>=2.0"
    ],
    "instructions": "Setup instructions..."  # User-facing docs
}
```

#### AgentContext
```python
@dataclass
class AgentContext:
    project_name: str                 # e.g., "Task Manager"
    project_description: str          # Full description
    requirements: List[str]           # Feature list
    tech_stack: Dict[str, str]       # {backend, frontend, db, etc}
    constraints: List[str]            # Time, budget, etc.
    previous_artifacts: Dict[str, Any] = None  # From other agents
    task_description: str = ""        # Specific task details
```

---

### 3. LLM Integration

**Location:** `llms/manager.py`

```python
async def call_llm(
    role: str,                        # Agent role from system_prompts.json
    user_prompt: str,                 # Your prompt to the LLM
    model: Optional[str] = None       # Override default model
) -> str:
    """
    Call LLM with role-specific system prompt.
    
    Args:
        role: Key from system_prompts.json (e.g., "backend_agent")
        user_prompt: What you want the LLM to generate
        model: Optional model override
        
    Returns:
        LLM response string
        
    Example:
        code = await call_llm(
            role="backend_agent",
            user_prompt="Create a User model in SQLAlchemy"
        )
    """
```

**Available Roles (from system_prompts.json):**
- `backend_agent`
- `frontend_agent`
- `devops_agent`
- `testing_agent`
- `github_coordinator`
- `ml_dl_engineer`
- `master_orchestrator`
- `cicd_integration`

---

### 4. Task Parser

**Location:** `orchestrator/task_parser.py`

```python
class TaskParser:
    """Parse natural language into structured tasks."""
    
    def parse_natural_language(self, description: str) -> List[Task]:
        """
        Convert project description to tasks.
        
        Args:
            description: Natural language project description
            
        Returns:
            List of Task objects with dependencies
            
        Example:
            parser = TaskParser()
            tasks = parser.parse_natural_language(
                "Build a web app with login and dashboard"
            )
            # Returns: [
            #   Task(name="auth", dependencies=[], ...),
            #   Task(name="dashboard", dependencies=["auth"], ...)
            # ]
        """
    
    def create_task_graph(self, tasks: List[Task]) -> Dict[str, Task]:
        """Create dependency graph from tasks."""
```

---

### 5. Master Orchestrator

**Location:** `orchestrator/master_orchestrator.py`

```python
class MasterOrchestrator:
    """Coordinate all agents and manage dependencies."""
    
    async def orchestrate(
        self, 
        description: str,
        tech_stack: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Execute all agents and assemble final project.
        
        Args:
            description: Project description
            tech_stack: {backend, frontend, database, deployment}
            
        Returns:
            Complete project structure with all artifacts
        """
```

---

### 6. Validation

**Location:** `validation/security_scanner.py`

```python
class SecurityScanner:
    """Detect vulnerabilities in generated code."""
    
    def scan_file(self, content: str) -> List[SecurityIssue]:
        """
        Scan code for vulnerabilities.
        
        Returns:
            List of detected issues with CWE numbers
        """

class ValidationEngine:
    """Run all validation checks."""
    
    async def validate_project(
        self,
        artifacts: Dict[str, Any]
    ) -> ValidationReport:
        """Validate entire project."""
```

---

## Common Patterns

### Pattern 1: Calling LLM in Your Agent

```python
async def perform(self, task: str, context: Dict) -> AgentResult:
    from llms.manager import call_llm
    
    # Build your prompt
    prompt = f"""
    Create a {context.get('framework')} REST API for {task}
    Requirements: {context.get('requirements')}
    """
    
    # Call LLM with your role
    code = await call_llm(
        role="backend_agent",
        user_prompt=prompt
    )
    
    # Parse response
    files = parse_code_blocks(code)
    
    return AgentResult(
        success=True,
        outputs=["Generated REST API endpoints"],
        artifacts={
            "files": files,
            "metadata": {...},
            "dependencies": ["fastapi"]
        }
    )
```

### Pattern 2: Accessing Agent Context

```python
async def perform(self, task: str, context: Dict) -> AgentResult:
    project_name = context.get("project_name")
    requirements = context.get("requirements", [])
    previous_api_spec = context.get("previous_artifacts", {}).get("api_spec")
    
    # Use this information to generate better code
    prompt = f"""
    For {project_name}, create components for:
    {', '.join(requirements)}
    
    Known API endpoints: {previous_api_spec}
    """
```

### Pattern 3: Returning Multiple Files

```python
return AgentResult(
    success=True,
    outputs=["Created auth module", "Added JWT validation"],
    artifacts={
        "files": {
            "src/auth/jwt.py": jwt_code,
            "src/auth/models.py": models_code,
            "src/auth/__init__.py": init_code,
            "tests/test_auth.py": test_code
        },
        "metadata": {
            "module": "auth",
            "submodules": ["jwt", "models"],
            "has_tests": True
        },
        "dependencies": ["python-jose", "passlib"],
        "instructions": "Set JWT_SECRET in .env"
    }
)
```

### Pattern 4: Error Handling

```python
async def perform(self, task: str, context: Dict) -> AgentResult:
    try:
        # Your logic
        result = await some_operation()
        
        return AgentResult(success=True, outputs=["Success"])
        
    except ValueError as e:
        return AgentResult(
            success=False,
            error=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        return AgentResult(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )
```

---

## Testing Your Agent

```python
# tests/test_custom_agent.py
import pytest
import asyncio
from agents import YourCustomAgent, AgentContext

@pytest.mark.asyncio
async def test_agent_success():
    agent = YourCustomAgent()
    
    context = AgentContext(
        project_name="Test Project",
        project_description="Test description",
        requirements=["Feature 1"],
        tech_stack={"backend": "fastapi"},
        constraints=[],
        task_description="Create test"
    )
    
    result = await agent.run("Test task", context)
    
    assert result.success == True
    assert len(result.outputs) > 0
    assert "files" in result.artifacts

@pytest.mark.asyncio
async def test_agent_error_handling():
    agent = YourCustomAgent()
    
    context = AgentContext(
        project_name="Test",
        project_description="",
        requirements=[],
        tech_stack={},
        constraints=[]
    )
    
    result = await agent.run("Invalid task", context)
    # Should handle gracefully
```

Run with: `pytest tests/test_custom_agent.py -v`

---

## Environment Variables

Set these before running agents:

```bash
# LLM Provider
export LLM_PROVIDER=openai  # or huggingface
export OPENAI_API_KEY=sk-...
export HUGGINGFACE_API_KEY=hf_...

# Optional
export LLM_MODEL=gpt-4-turbo
export AGENT_TIMEOUT=300
```

---

## File Organization

Your custom agent should follow this structure:

```
agents/
├── __init__.py              # Must export your agents
├── base_agent.py            # Base class (don't modify)
├── specialist_agents.py     # Your custom agent implementations
└── utils.py                 # Helper functions (optional)

prompts/
├── system_prompts.json      # Update with your prompts
└── your_custom_role.md      # Optional custom prompts

tests/
├── test_agents.py           # Update with your tests
└── test_your_agent.py       # Your agent-specific tests
```

---

## Troubleshooting

### Issue: Agent times out
**Solution:** Increase `timeout_seconds` in AgentConfig or optimize LLM call

### Issue: LLM not responding
**Solution:** Check `LLM_PROVIDER` and API keys are set correctly

### Issue: Files not being created
**Solution:** Ensure `artifacts["files"]` is a dictionary with string values

### Issue: Dependencies not tracked
**Solution:** Always populate `artifacts["dependencies"]` list

### Issue: Integration tests fail
**Solution:** Run `pytest tests/ -v` to see specific failures

---

## Deployment

Once your agents are ready:

1. Update `agents/__init__.py` with exports
2. Run tests: `pytest tests/ -v`
3. Verify all 17+ tests pass
4. Push to branch
5. Create PR for code review
6. Merge to main after approval

---

**Keep this reference handy while developing your custom agents!**

Questions? Check ARCHITECTURE.md for system-level details.
