# MVP Factory Architecture

## Overview

MVP Factory is an AI-powered code generation system that orchestrates specialist LLM agents to build complete MVP applications from natural language descriptions. The system combines task parsing, role-based agents, validation frameworks, and LLM orchestration.

## Core Components

### 1. Task Parser (`orchestrator/task_parser.py`)
Converts natural language project descriptions into structured tasks.

**Key Classes:**
- `TaskType`: Enum of task categories (CREATE_API, CREATE_UI, SETUP_DATABASE, IMPLEMENT_AUTH, ADD_FEATURE, DEPLOY, TEST, INTEGRATE_SERVICE)
- `Task`: Dataclass representing a structured development task with dependencies, time estimates, and agent assignments
- `TaskParser`: Parses descriptions using regex patterns and maps to agent types

**Usage:**
```python
from orchestrator.task_parser import parse_project_description

description = "Create a task manager with auth, database, and React UI"
result = parse_project_description(description)
# Returns: {
#   "parsed_tasks": [...],
#   "task_graph": {"nodes": [...], "edges": [...]},
#   "time_estimate": {"estimated_minutes": ...},
#   "agents_required": [...]
# }
```

### 2. Specialist Agents (`agents/`)

#### Base Agent (`agents/base_agent.py`)
Abstract base class for all agents.

**Key Classes:**
- `AgentConfig`: Configuration for agent behavior (name, role, capabilities, timeout)
- `AgentResult`: Result containing success status, outputs, artifacts, and errors
- `BaseAgent`: Abstract class with `run()` wrapper and `perform()` abstract method

#### Specialist Agents (`agents/specialist_agents.py`)
Role-specific implementations:

- **BackendAgent**: REST APIs, databases, business logic
- **FrontendAgent**: UI components, styling, state management
- **DevOpsAgent**: Infrastructure, CI/CD, deployment
- **TestingAgent**: Test suites, validation frameworks

**Usage:**
```python
from agents import AgentFactory, AgentRole, AgentContext

context = AgentContext(
    project_name="My App",
    project_description="Task management app",
    requirements=["Auth", "CRUD API"],
    tech_stack={"backend": "fastapi", "frontend": "nextjs"},
    constraints=[]
)

backend_agent = AgentFactory.create_agent(AgentRole.BACKEND_ENGINEER)
result = await backend_agent.execute("Create user authentication API", context)
```

### 3. Master Orchestrator (`orchestrator/master_orchestrator.py`)
Coordinates task execution across all agents.

**Key Workflow:**
1. Parse project description into tasks
2. Build task dependency graph
3. Determine optimal execution order (topological sort)
4. Execute tasks in parallel where possible
5. Assemble artifacts into a cohesive project

**Usage:**
```python
from orchestrator.master_orchestrator import create_mvp

result = await create_mvp(
    project_description="Build a blogging platform",
    tech_stack={"backend": "fastapi", "frontend": "nextjs"},
    requirements=["User authentication", "Comments", "Search"]
)
# Returns orchestration result with artifacts and metadata
```

### 4. Validation Framework (`validation/`)

#### Code Validator (`validation/validator.py`)
Validates code for quality and security.

**Validators:**
- `SecurityValidator`: Hardcoded secrets, SQL injection, XSS
- `CodeQualityValidator`: Python/JavaScript best practices
- `ValidationEngine`: Orchestrates all validators

**Usage:**
```python
from validation.validator import validate_code_snippet

code = "def process(): pass"
result = validate_code_snippet(code, "python")
# Returns validation summary with passed/failed checks
```

#### Security Scanner (`validation/security_scanner.py`)
Advanced vulnerability detection.

**Features:**
- CWE-based vulnerability detection
- LLM fingerprint detection
- Security reporting

**Usage:**
```python
from validation.security_scanner import scan_for_security_vulnerabilities

code = "api_key = 'hardcoded'"
result = scan_for_security_vulnerabilities("test.py", code)
# Returns vulnerabilities found and risk level
```

### 5. LLM Integration (`llms/`)

#### Manager (`llms/manager.py`)
Role-aware LLM provider abstraction.

**Features:**
- Automatic system prompt loading from `prompts/system_prompts.json`
- Provider selection (OpenAI or Hugging Face)
- Role-based prompt composition

**Usage:**
```python
from llms.manager import call_llm, LLMCallOptions

response = call_llm(
    role="backend_agent",
    user_prompt="Create FastAPI endpoint for users",
    opts=LLMCallOptions(temperature=0.2, max_tokens=2048)
)
# Returns: {"text": "...", "raw": {...}}
```

#### System Prompts (`prompts/system_prompts.json`)
Role-specific system prompts for each agent:
- master_orchestrator
- github_coordinator
- ml_dl_engineer
- backend_agent
- ui_ux_engineer
- devops_engineer
- cicd_integration
- testing_validation

## Testing

All components are tested with pytest:

```bash
cd mvp-factory
pytest tests/ -v
```

**Test Coverage:**
- Task parser: 8 tests (descriptions, graph creation, time estimation)
- Validation framework: 9 tests (engine, security, LLM detection)
- All tests pass: 17/17 ✅

## Workflow Example

```python
import asyncio
from orchestrator.master_orchestrator import create_mvp

async def main():
    result = await create_mvp(
        project_description="""
        Create a collaborative task management app with:
        - User authentication (JWT)
        - REST API for CRUD operations
        - React frontend with real-time updates
        - PostgreSQL database
        - Deployment to Vercel
        - Comprehensive test suite
        """,
        tech_stack={
            "backend": "fastapi",
            "frontend": "nextjs",
            "database": "postgresql",
            "deployment": "vercel"
        },
        requirements=[
            "User authentication",
            "Task CRUD",
            "Real-time collaboration",
            "Mobile responsive"
        ]
    )
    
    if result["success"]:
        print("MVP generated successfully!")
        print(f"Total tasks: {result['report']['task_breakdown']['total']}")
        print(f"Artifacts: {list(result['artifacts'].keys())}")
    else:
        print(f"Generation failed: {result['errors']}")

asyncio.run(main())
```

## Configuration

### Environment Variables
- `LLM_PROVIDER`: Provider selection ('openai', 'hf', auto-detect)
- `OPENAI_API_KEY`: OpenAI API key
- `HF_MODEL_PATH` or `HF_TOKEN`: Hugging Face configuration
- `OPENAI_DEFAULT_MODEL`: Default model (e.g., 'gpt-4o-mini')

### System Prompts
Edit `prompts/system_prompts.json` to customize agent behavior.

## Project Structure
```
mvp-factory/
├── agents/                 # Specialist agent implementations
│   ├── __init__.py        # Module exports
│   ├── base_agent.py      # Abstract base class
│   └── specialist_agents.py # Concrete agents
├── orchestrator/          # Task orchestration
│   ├── task_parser.py     # NL -> Tasks conversion
│   ├── master_orchestrator.py # Execution coordinator
│   └── coordination.py     # Task coordination
├── llms/                  # LLM integration
│   ├── manager.py         # Provider abstraction
│   ├── prompt_engineer.py # Prompt optimization
│   └── eval.py            # Evaluation harness
├── validation/            # Code quality & security
│   ├── validator.py       # Multi-validator engine
│   ├── security_scanner.py # Vulnerability detection
│   ├── code_quality.py    # Style & quality checks
│   └── validator.py       # Result formatting
├── prompts/               # System prompts for agents
│   ├── system_prompts.json # Role-specific prompts
│   └── *.md               # Individual agent prompts
├── tests/                 # Test suite
│   ├── test_task_parser.py
│   ├── test_agents.py
│   ├── test_validation.py
│   └── test_orchestrator.py
└── scripts/               # Utility scripts
    ├── generate_mvp.sh    # Generate MVP from description
    ├── run_tests.sh       # Test runner
    ├── prompt_style_lint.py # Prompt validation
    └── generate_role_jsonl.py # Fine-tune data generation
```

## Development Roadmap

### Completed ✅
- Task parsing from natural language
- Specialist agent framework
- Validation framework (security + quality)
- LLM provider abstraction
- Master orchestrator structure
- System prompt management
- Complete test coverage (17 tests)

### Next Steps (Requires User Input)
1. **Fine-tuning**: Generate role-specific fine-tune datasets using `scripts/generate_role_jsonl.py`
2. **LLM Integration**: Connect to OpenAI or Hugging Face with credentials
3. **Custom Prompts**: Refine system prompts in `prompts/system_prompts.json`
4. **Agent Extensions**: Add new specialist agents as needed
5. **Deployment**: Package and deploy the MVP Factory service

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

3. **Set up LLM provider:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # or
   export HF_MODEL_PATH="meta-llama/Llama-2-7b"
   ```

4. **Generate an MVP:**
   ```bash
   python scripts/generate_mvp.sh "Create a todo app with auth and database"
   ```

## CI/CD

GitHub Actions pipeline (`mvp-factory/.github/workflows/ci.yml`):
- Prompt style linting
- Unit tests + coverage
- Validation framework tests
- Docker image build
- Documentation deployment

All tests must pass before merging to main.

---

**Last Updated:** December 23, 2025  
**Version:** 1.0.0  
**Status:** Ready for LLM Integration
