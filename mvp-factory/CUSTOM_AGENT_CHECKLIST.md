# Custom Agent Implementation Checklist

## Pre-Development Setup

- [ ] Clone repository and create feature branch: `git checkout -b feat/custom-agents`
- [ ] Create virtual environment: `python -m venv venv && source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify existing tests pass: `pytest tests/ -v`
- [ ] Read ARCHITECTURE.md for system overview
- [ ] Read AGENT_SPECIFICATION.md for detailed specs
- [ ] Read AGENT_API_REFERENCE.md for API details

---

## For Each Custom Agent (Backend, Frontend, DevOps, Testing)

### Design Phase

- [ ] Review relevant section in AGENT_SPECIFICATION.md
- [ ] Document agent's specific responsibilities
- [ ] List all expected input parameters (from AgentContext)
- [ ] List all expected output artifacts
- [ ] Identify any dependencies on other agents
- [ ] Design error handling strategy
- [ ] Draft system prompt for LLM integration

### Implementation Phase

- [ ] Create class inheriting from `BaseAgent`
- [ ] Implement `async perform()` method
- [ ] Add type hints to all methods/parameters
- [ ] Import `call_llm()` from `llms.manager`
- [ ] Build prompts for LLM calls
- [ ] Parse LLM responses into structured format
- [ ] Create file dictionary in artifacts
- [ ] Populate metadata about generated code
- [ ] List all dependencies
- [ ] Add helpful instructions for users
- [ ] Implement proper error handling
- [ ] Add logging statements for debugging

### Code Quality Phase

- [ ] Run black formatter: `black agents/`
- [ ] Run flake8 linter: `flake8 agents/`
- [ ] Run mypy type checker: `mypy agents/`
- [ ] No hardcoded secrets or API keys
- [ ] No debug print statements
- [ ] Docstrings on all functions
- [ ] Comments explaining complex logic
- [ ] PEP 8 style compliance

### Testing Phase

- [ ] Create test file: `tests/test_custom_agent_name.py`
- [ ] Write unit tests for each method
- [ ] Test with valid AgentContext
- [ ] Test with missing/invalid context
- [ ] Test successful execution path
- [ ] Test error handling path
- [ ] Test artifact structure
- [ ] Test timeout behavior
- [ ] Run: `pytest tests/test_custom_agent_name.py -v`
- [ ] Achieve >80% code coverage: `pytest --cov=agents`
- [ ] All existing tests still pass: `pytest tests/ -q`

### Documentation Phase

- [ ] Add docstring to class with purpose
- [ ] Document all constructor parameters
- [ ] Document async perform() method
- [ ] Document expected outputs
- [ ] Add usage example in docstring
- [ ] Create README.md for agent (optional)
- [ ] Add comments explaining LLM prompt design
- [ ] Document any assumptions or constraints

### Integration Phase

- [ ] Update `agents/__init__.py` to export your agent
- [ ] Update `llms/manager.py` if using new system prompts
- [ ] Test imports: `python -c "from agents import YourAgent"`
- [ ] Update `prompts/system_prompts.json` with new roles
- [ ] Verify MasterOrchestrator can instantiate your agent
- [ ] Run integration tests with orchestrator

### Final Validation

- [ ] All 17+ original tests still pass
- [ ] New agent tests pass (min 5 tests per agent)
- [ ] Total coverage >= 80%
- [ ] No import errors
- [ ] No type checking errors
- [ ] Agent can be instantiated
- [ ] Agent can execute sample tasks
- [ ] Error handling works as expected
- [ ] Dependencies properly listed
- [ ] Code follows project conventions

---

## Checklist Template for Each Agent

```
Agent Name: ___________________

Design Phase:
- [ ] Responsibilities documented
- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error cases identified
- [ ] System prompt drafted

Implementation:
- [ ] Class created (inherits BaseAgent)
- [ ] perform() method implemented
- [ ] LLM integration added
- [ ] Error handling implemented
- [ ] Logging added

Code Quality:
- [ ] Black formatting applied
- [ ] No linting errors
- [ ] Type hints complete
- [ ] No hardcoded secrets
- [ ] Docstrings added

Testing:
- [ ] Test file created
- [ ] 5+ tests written
- [ ] Coverage >= 80%
- [ ] All tests pass
- [ ] Existing tests still pass

Integration:
- [ ] Exported in agents/__init__.py
- [ ] System prompt added
- [ ] Imports verified
- [ ] Works with MasterOrchestrator

Status: ❌ (Not started) → 🟡 (In Progress) → ✅ (Complete)
```

---

## Implementation Order

**Recommended sequence (fastest to slowest):**

1. **TestingAgent** (10-15 hours)
   - Simplest: generates test code
   - Fewer dependencies on other agents
   - Clear input/output contract

2. **BackendAgent** (15-20 hours)
   - Core system: APIs, models, auth
   - Foundation for everything else
   - Can be validated independently

3. **FrontendAgent** (15-20 hours)
   - Depends on BackendAgent output
   - Component generation
   - Styling integration

4. **DevOpsAgent** (10-15 hours)
   - Depends on all other agents
   - Infrastructure code
   - Deployment configuration

**Total estimated time: 50-70 hours** (may vary based on LLM fine-tuning quality)

---

## Code Example Structure

Your agent should follow this template:

```python
# agents/specialist_agents.py (add to existing file)

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import asyncio
from .base_agent import BaseAgent, AgentConfig, AgentResult
from llms.manager import call_llm

class YourCustomAgent(BaseAgent):
    """
    One-line description of what this agent does.
    
    This agent is responsible for:
    - Responsibility 1
    - Responsibility 2
    - Responsibility 3
    """
    
    def __init__(self):
        """Initialize the agent."""
        config = AgentConfig(
            name="Your Agent Name",
            role="your_agent_role",
            capabilities=[
                "capability_1",
                "capability_2"
            ],
            timeout_seconds=300
        )
        super().__init__(config)
    
    async def perform(
        self, 
        task: str, 
        context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute the agent's main logic.
        
        Args:
            task: What to generate (e.g., "Create REST APIs")
            context: Project context with requirements
            
        Returns:
            AgentResult with generated artifacts
        """
        try:
            # 1. Extract context
            project_name = context.get("project_name", "")
            requirements = context.get("requirements", [])
            tech_stack = context.get("tech_stack", {})
            
            # 2. Build prompt
            prompt = f"""
            For project '{project_name}':
            Requirements: {', '.join(requirements)}
            Tech Stack: {tech_stack}
            
            Task: {task}
            
            Generate production-ready code...
            """
            
            # 3. Call LLM
            response = await call_llm(
                role="your_role",
                user_prompt=prompt
            )
            
            # 4. Parse response
            files = self._parse_response(response)
            
            # 5. Validate output
            if not files:
                return AgentResult(
                    success=False,
                    error="LLM failed to generate code"
                )
            
            # 6. Return structured result
            return AgentResult(
                success=True,
                outputs=[
                    "Generated component A",
                    "Generated component B"
                ],
                artifacts={
                    "files": files,
                    "metadata": {
                        "type": "your_type",
                        "components": list(files.keys())
                    },
                    "dependencies": ["dep1", "dep2"],
                    "instructions": "Setup instructions here"
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Agent failed: {str(e)}"
            )
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response into file dictionary."""
        # Extract code blocks from response
        files = {}
        # Implementation here
        return files
```

---

## Testing Template

```python
# tests/test_your_custom_agent.py

import pytest
from agents import YourCustomAgent, AgentContext

@pytest.fixture
def agent():
    """Create agent instance."""
    return YourCustomAgent()

@pytest.fixture
def sample_context():
    """Create sample context."""
    return AgentContext(
        project_name="Test Project",
        project_description="Test description",
        requirements=["Feature 1", "Feature 2"],
        tech_stack={"backend": "fastapi", "database": "postgresql"},
        constraints=["Production-ready"],
        task_description="Create test module"
    )

@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test agent initializes correctly."""
    assert agent.config.name is not None
    assert agent.config.role is not None

@pytest.mark.asyncio
async def test_successful_execution(agent, sample_context):
    """Test successful task execution."""
    result = await agent.run("Create sample", sample_context)
    
    assert result.success == True
    assert len(result.outputs) > 0
    assert "files" in result.artifacts
    assert len(result.artifacts["files"]) > 0

@pytest.mark.asyncio
async def test_artifact_structure(agent, sample_context):
    """Test output artifact structure."""
    result = await agent.run("Generate code", sample_context)
    
    artifacts = result.artifacts
    assert "files" in artifacts
    assert "metadata" in artifacts
    assert "dependencies" in artifacts
    assert isinstance(artifacts["files"], dict)
    assert isinstance(artifacts["dependencies"], list)

@pytest.mark.asyncio
async def test_error_handling(agent):
    """Test error handling with invalid context."""
    invalid_context = AgentContext(
        project_name="",
        project_description="",
        requirements=[],
        tech_stack={},
        constraints=[]
    )
    
    result = await agent.run("Invalid", invalid_context)
    # Should handle gracefully

@pytest.mark.asyncio
async def test_timeout_handling(agent, sample_context):
    """Test timeout configuration."""
    assert agent.config.timeout_seconds is not None
    assert agent.config.timeout_seconds > 0
```

---

## Common Mistakes to Avoid

❌ **Don't:**
- Hardcode API keys or secrets in code
- Forget to inherit from BaseAgent
- Return wrong data types in AgentResult
- Skip type hints
- Ignore error cases
- Make synchronous calls (use `async/await`)
- Return empty artifacts
- Forget to document code
- Skip tests
- Modify base_agent.py

✅ **Do:**
- Use environment variables for secrets
- Follow the AgentResult contract
- Add comprehensive type hints
- Handle all error cases
- Use async/await consistently
- Populate all artifact fields
- Add docstrings
- Write unit + integration tests
- Keep base_agent.py unchanged
- Test with real agentcontext data

---

## Validation Checklist Before Submission

- [ ] Code passes all linters (black, flake8, mypy)
- [ ] All tests pass (>=5 per agent)
- [ ] Total coverage >= 80%
- [ ] No import errors
- [ ] Agent instantiates without errors
- [ ] Agent executes sample task
- [ ] Artifacts have correct structure
- [ ] Dependencies listed accurately
- [ ] Error handling works
- [ ] No hardcoded secrets
- [ ] Docstrings complete
- [ ] Ready for code review

---

## Submission Steps

1. **Create feature branch:**
   ```bash
   git checkout -b feat/custom-agents
   ```

2. **Commit your work:**
   ```bash
   git add agents/ prompts/ tests/
   git commit -m "feat: implement custom agents"
   ```

3. **Run final validation:**
   ```bash
   pytest tests/ -v --cov=agents
   black agents/
   flake8 agents/
   mypy agents/
   ```

4. **Push to GitHub:**
   ```bash
   git push origin feat/custom-agents
   ```

5. **Create pull request** with description of agents

---

## Estimated Effort

| Task | Backend | Frontend | DevOps | Testing |
|------|---------|----------|--------|---------|
| Design | 2h | 2h | 2h | 1h |
| Implementation | 8h | 8h | 6h | 6h |
| Code Quality | 1h | 1h | 1h | 1h |
| Testing | 2h | 2h | 2h | 2h |
| Integration | 2h | 2h | 2h | 1h |
| **Total** | **15h** | **15h** | **13h** | **11h** |

**Grand Total: ~54 hours**

---

## Resources Available

- `ARCHITECTURE.md` - System design overview
- `AGENT_SPECIFICATION.md` - Detailed agent requirements
- `AGENT_API_REFERENCE.md` - API documentation
- `prompts/system_prompts.json` - Example prompts
- `tests/test_agents.py` - Reference test implementations
- `agents/base_agent.py` - Base class (read-only)
- `orchestrator/master_orchestrator.py` - Integration point

---

**Good luck with implementation! You've got this. 🚀**

Feel free to reference these docs as you build your custom agents.
