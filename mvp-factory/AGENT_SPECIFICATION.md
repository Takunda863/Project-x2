# MVP Factory - Final Architecture & Agent Specifications

## System Architecture

### High-Level Flow

```
User Input (Natural Language)
        ↓
    [Task Parser]
        ↓
    Task Graph + Dependencies
        ↓
    [Master Orchestrator]
        ↓
    ┌─────────────────────────────────┐
    │   Parallel Agent Execution      │
    │  ┌──────────────────────────┐   │
    │  │ BackendAgent (FastAPI)   │   │
    │  │ - REST APIs              │   │
    │  │ - Database Schema        │   │
    │  │ - Business Logic         │   │
    │  └──────────────────────────┘   │
    │  ┌──────────────────────────┐   │
    │  │ FrontendAgent (React)    │   │
    │  │ - Components             │   │
    │  │ - Styling                │   │
    │  │ - State Management       │   │
    │  └──────────────────────────┘   │
    │  ┌──────────────────────────┐   │
    │  │ DevOpsAgent              │   │
    │  │ - Infrastructure         │   │
    │  │ - CI/CD Pipelines        │   │
    │  │ - Deployment             │   │
    │  └──────────────────────────┘   │
    │  ┌──────────────────────────┐   │
    │  │ TestingAgent             │   │
    │  │ - Unit Tests             │   │
    │  │ - Integration Tests      │   │
    │  │ - E2E Tests              │   │
    │  └──────────────────────────┘   │
    └─────────────────────────────────┘
        ↓
    [Validation Layer]
    - Security Scanner
    - Code Quality Checks
        ↓
    [Artifact Assembly]
    - Project Structure
    - File Organization
    - README Generation
        ↓
    Complete MVP Codebase
```

---

## Agent Contract Specification

### Base Interface

All agents must inherit from `BaseAgent` and implement this interface:

```python
# Location: agents/base_agent.py (existing)

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

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
    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Execute agent - handles timeouts, logging, error handling"""
        # Wrapper implementation already exists
    
    @abstractmethod
    async def perform(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Implement this - core agent logic"""
```

### Context Object (Input Specification)

All agents receive an `AgentContext` object:

```python
@dataclass
class AgentContext:
    project_name: str                    # e.g., "Task Manager"
    project_description: str             # Full project description
    requirements: List[str]              # Feature requirements
    tech_stack: Dict[str, str]          # {backend, frontend, db, deployment}
    constraints: List[str]               # Time, budget, etc.
    previous_artifacts: Dict[str, Any]  # Output from previous agents
    task_description: str                # Specific task for this agent
```

### Agent Result Output (Output Specification)

All agents return an `AgentResult`:

```python
AgentResult(
    success: bool                        # Was execution successful?
    outputs: List[str]                  # Generated code/text
    artifacts: Dict[str, Any] {          # Organized deliverables
        "files": {
            "path/to/file.py": "content",
            "path/to/file.js": "content"
        },
        "metadata": {
            "framework": "fastapi",
            "description": "..."
        },
        "dependencies": ["package1", "package2"],
        "instructions": "Setup/deployment instructions"
    }
    error: Optional[str]                # Error message if failed
)
```

---

## Individual Agent Specifications

### 1. BACKEND AGENT

**Purpose:** Generate REST APIs, database schemas, business logic, authentication systems

**Input:**
```python
task_description = "Create user authentication with JWT and database schema for users table"

context = AgentContext(
    project_name="Task Manager",
    project_description="Collaborative task management app",
    requirements=["User authentication", "Task CRUD", "Real-time sync"],
    tech_stack={
        "backend": "fastapi",
        "database": "postgresql",
        "auth": "jwt"
    },
    constraints=["Must use SQLAlchemy ORM", "Production-ready"],
    task_description=task_description
)
```

**Expected Output:**
```python
AgentResult(
    success=True,
    outputs=[
        "Generated user authentication module with JWT",
        "Created database models using SQLAlchemy",
        "Implemented password hashing with bcrypt"
    ],
    artifacts={
        "files": {
            "src/auth/models.py": "class User(Base): ...",
            "src/auth/schemas.py": "class UserCreate(BaseModel): ...",
            "src/auth/routes.py": "@router.post('/login'): ...",
            "src/auth/security.py": "def get_password_hash(): ...",
            "src/database/models.py": "class Task(Base): ..."
        },
        "metadata": {
            "framework": "fastapi",
            "orm": "sqlalchemy",
            "auth_method": "jwt",
            "password_hashing": "bcrypt"
        },
        "dependencies": [
            "fastapi>=0.95.0",
            "sqlalchemy>=2.0",
            "pydantic>=2.0",
            "python-jose[cryptography]",
            "passlib[bcrypt]",
            "psycopg2-binary"
        ],
        "instructions": "1. Create PostgreSQL database\n2. Run migrations\n3. Set JWT_SECRET in .env"
    }
)
```

**Key Responsibilities:**
- ✅ REST API endpoint design (GET, POST, PUT, DELETE)
- ✅ Database schema design (tables, relationships, indexes)
- ✅ ORM model definitions (SQLAlchemy, Pydantic schemas)
- ✅ Authentication/Authorization (JWT, OAuth, role-based)
- ✅ Business logic implementation
- ✅ Error handling and validation
- ✅ API documentation (OpenAPI/Swagger)
- ✅ Environment configuration templates

**Code Quality Standards:**
- No hardcoded secrets (use environment variables)
- Proper error handling with specific HTTP status codes
- Input validation on all endpoints
- Logging at appropriate levels (info, warning, error)
- Type hints on all functions
- Docstrings for all modules and functions
- Follows PEP 8 style guide

---

### 2. FRONTEND AGENT

**Purpose:** Generate React components, styling, state management, UI logic

**Input:**
```python
task_description = "Create user login/register page with form validation and error handling"

context = AgentContext(
    project_name="Task Manager",
    project_description="Collaborative task management app",
    requirements=["Responsive design", "Form validation", "Error messages"],
    tech_stack={
        "frontend": "nextjs",
        "styling": "tailwind",
        "state": "zustand"
    },
    constraints=["Mobile-first", "Accessibility WCAG 2.1 AA"],
    task_description=task_description,
    previous_artifacts={
        "backend_apis": [
            {"method": "POST", "path": "/auth/login", "body": "email, password"},
            {"method": "POST", "path": "/auth/register", "body": "email, password, name"}
        ]
    }
)
```

**Expected Output:**
```python
AgentResult(
    success=True,
    outputs=[
        "Created login page component with form validation",
        "Implemented error boundary for error handling",
        "Added responsive design for mobile/tablet/desktop"
    ],
    artifacts={
        "files": {
            "src/components/auth/LoginForm.tsx": "export function LoginForm(): JSX.Element { ... }",
            "src/components/auth/RegisterForm.tsx": "export function RegisterForm(): JSX.Element { ... }",
            "src/pages/auth/login.tsx": "export default function LoginPage(): JSX.Element { ... }",
            "src/pages/auth/register.tsx": "export default function RegisterPage(): JSX.Element { ... }",
            "src/hooks/useAuth.ts": "export function useAuth(): { ... }",
            "src/store/authStore.ts": "export const useAuthStore = create((set) => ({ ... }))",
            "src/components/common/ErrorBoundary.tsx": "export class ErrorBoundary extends React.Component { ... }",
            "src/styles/auth.module.css": ".loginContainer { ... }"
        },
        "metadata": {
            "framework": "nextjs",
            "styling": "tailwind",
            "state_management": "zustand",
            "components": ["LoginForm", "RegisterForm", "ErrorBoundary"],
            "responsive": ["mobile", "tablet", "desktop"],
            "accessibility": "WCAG 2.1 AA"
        },
        "dependencies": [
            "next>=14.0",
            "react>=18.0",
            "zustand>=4.0",
            "tailwindcss>=3.0",
            "react-hook-form>=7.0",
            "zod>=3.0"
        ],
        "instructions": "1. Install dependencies\n2. Copy components to src/components/\n3. Configure Tailwind in tailwind.config.js\n4. Update next.config.js routing"
    }
)
```

**Key Responsibilities:**
- ✅ React component creation (functional, hooks-based)
- ✅ Form handling with validation
- ✅ State management integration
- ✅ Styling (Tailwind CSS classes)
- ✅ Responsive design (mobile-first)
- ✅ Accessibility (ARIA labels, semantic HTML, keyboard navigation)
- ✅ Error handling and user feedback
- ✅ API integration (fetch/axios calls)
- ✅ Performance optimization (lazy loading, memoization)

**Code Quality Standards:**
- TypeScript with strict mode
- Proper type definitions for all props
- No `any` types (use `unknown` and narrow types)
- ESLint + Prettier formatting
- Component composition over inheritance
- Prop drilling minimization (use context/store)
- Atomic component design (atoms → molecules → organisms)
- Accessibility first (keyboard navigation, screen readers)
- Mobile-responsive (tested at 320px, 768px, 1920px widths)

---

### 3. DEVOPS AGENT

**Purpose:** Generate infrastructure code, CI/CD pipelines, deployment configurations

**Input:**
```python
task_description = "Create Docker setup for FastAPI + PostgreSQL + Next.js with GitHub Actions CI/CD for Vercel deployment"

context = AgentContext(
    project_name="Task Manager",
    project_description="Collaborative task management app",
    requirements=["Docker containerization", "GitHub Actions CI", "Vercel deployment"],
    tech_stack={
        "deployment": "vercel",
        "ci_cd": "github_actions",
        "containerization": "docker"
    },
    constraints=["Free tier eligible", "Production-ready"],
    task_description=task_description
)
```

**Expected Output:**
```python
AgentResult(
    success=True,
    outputs=[
        "Created Docker setup for multi-service architecture",
        "Implemented GitHub Actions workflow",
        "Generated deployment configuration for Vercel"
    ],
    artifacts={
        "files": {
            "Dockerfile.backend": "FROM python:3.11 ...",
            "Dockerfile.frontend": "FROM node:18 ...",
            "docker-compose.yml": "version: '3.8'\nservices: ...",
            ".github/workflows/ci.yml": "name: CI Pipeline\non: [push, pull_request] ...",
            ".github/workflows/deploy.yml": "name: Deploy\non: [push:main] ...",
            "vercel.json": "{\n  \"buildCommand\": \"npm run build\",\n  \"outputDirectory\": \".next\"\n}",
            "backend/.dockerignore": "...",
            "backend/docker-entrypoint.sh": "#!/bin/bash\nuvicorn main:app ...",
            "nginx.conf": "upstream backend { ... }",
            "scripts/deploy.sh": "#!/bin/bash\nvercel deploy --prod"
        },
        "metadata": {
            "deployment_target": "vercel",
            "ci_cd": "github_actions",
            "containerization": "docker",
            "services": ["backend", "frontend", "postgres"],
            "environments": ["development", "staging", "production"]
        },
        "dependencies": {
            "docker": "latest",
            "docker-compose": "2.x",
            "github_actions": "N/A",
            "vercel_cli": "latest"
        },
        "instructions": "1. Create GitHub repository secrets (DB_PASSWORD, API_KEY)\n2. Push to main to trigger CI\n3. Vercel auto-deploys on successful tests\n4. Local dev: docker-compose up"
    }
)
```

**Key Responsibilities:**
- ✅ Docker/Dockerfile creation (multi-stage builds, optimized layers)
- ✅ Docker Compose setup (local development environment)
- ✅ CI/CD pipeline creation (GitHub Actions, GitLab CI, etc.)
- ✅ Test automation in pipeline
- ✅ Build and push artifacts
- ✅ Deployment configuration (Vercel, AWS, Google Cloud, Azure)
- ✅ Environment management (.env templates, secrets)
- ✅ Database migration scripts
- ✅ Health checks and monitoring setup
- ✅ Rollback procedures

**Code Quality Standards:**
- Dockerfiles follow best practices (minimal base images, layer caching)
- Shell scripts have error handling (`set -e`)
- Configuration as code (IaC principles)
- No secrets in code/config (use environment variables)
- Proper logging configuration
- Health check endpoints defined
- Zero-downtime deployments where possible

---

### 4. TESTING AGENT

**Purpose:** Generate test suites, testing infrastructure, validation scripts

**Input:**
```python
task_description = "Create comprehensive test suite: unit tests for auth, integration tests for APIs, E2E tests for user flows"

context = AgentContext(
    project_name="Task Manager",
    project_description="Collaborative task management app",
    requirements=["80%+ code coverage", "Unit + integration + E2E tests", "CI integration"],
    tech_stack={
        "backend_testing": "pytest",
        "frontend_testing": "vitest",
        "e2e_testing": "playwright"
    },
    constraints=["Tests must run in CI under 5 minutes"],
    task_description=task_description,
    previous_artifacts={
        "backend_modules": ["auth", "tasks", "database"],
        "frontend_components": ["LoginForm", "TaskList", "TaskDetail"]
    }
)
```

**Expected Output:**
```python
AgentResult(
    success=True,
    outputs=[
        "Created pytest unit test suite with 40+ tests",
        "Implemented integration tests for API endpoints",
        "Set up Playwright E2E tests for user workflows"
    ],
    artifacts={
        "files": {
            "tests/unit/test_auth.py": "def test_hash_password(): ...",
            "tests/unit/test_models.py": "def test_user_model_creation(): ...",
            "tests/integration/test_auth_api.py": "def test_login_endpoint(client): ...",
            "tests/integration/test_task_api.py": "def test_create_task(client): ...",
            "tests/e2e/login.spec.ts": "test('User login flow', async ({ page }) => { ... })",
            "tests/e2e/task_workflow.spec.ts": "test('Complete task workflow', async ({ page }) => { ... })",
            "tests/conftest.py": "pytest fixtures and DB setup",
            "tests/frontend/auth.test.tsx": "describe('LoginForm', () => { ... })",
            "pytest.ini": "[pytest]\ntestpaths = tests",
            ".github/workflows/test.yml": "Run tests on every push"
        },
        "metadata": {
            "coverage_target": 80,
            "test_types": ["unit", "integration", "e2e"],
            "backend_framework": "pytest",
            "frontend_framework": "vitest",
            "e2e_framework": "playwright",
            "total_tests": 50
        },
        "dependencies": {
            "backend": ["pytest>=7.0", "pytest-cov", "pytest-asyncio", "httpx"],
            "frontend": ["vitest>=0.34", "@testing-library/react", "@testing-library/user-event"],
            "e2e": ["@playwright/test>=1.40"]
        },
        "instructions": "1. Install test dependencies\n2. Run pytest: pytest tests/ --cov\n3. Run frontend tests: npm run test\n4. Run E2E: npm run test:e2e\n5. Coverage report in htmlcov/index.html"
    }
)
```

**Key Responsibilities:**
- ✅ Unit tests (individual functions/classes)
- ✅ Integration tests (API endpoints, database interactions)
- ✅ End-to-end tests (user workflows)
- ✅ Test fixtures and mocking
- ✅ Code coverage measurement
- ✅ Performance benchmarks
- ✅ Security testing (OWASP, injection, etc.)
- ✅ Test documentation
- ✅ CI/CD test integration

**Code Quality Standards:**
- Clear test names (what, how, expected outcome)
- Arrange-Act-Assert pattern
- DRY principle (shared fixtures)
- Isolated tests (no test interdependencies)
- Fast execution (unit < 1s each)
- Deterministic (no flaky tests)
- >80% code coverage target
- Meaningful assertions with clear failure messages

---

## Data Flow & Integration Points

### Agent Execution Flow

```
1. INITIALIZATION
   ├─ Task Parser creates task list
   └─ Master Orchestrator creates AgentContext

2. PARALLEL EXECUTION (all agents run concurrently based on dependencies)
   ├─ BackendAgent.execute(context) → AgentResult (APIs, Models, Auth)
   ├─ FrontendAgent.execute(context) → AgentResult (Components, Pages, Hooks)
   ├─ DevOpsAgent.execute(context) → AgentResult (Docker, CI/CD, Deploy)
   └─ TestingAgent.execute(context) → AgentResult (Tests, Coverage)

3. ARTIFACT ASSEMBLY
   ├─ Extract files from all AgentResults
   ├─ Create directory structure
   ├─ Generate README from metadata
   └─ Create .env templates

4. VALIDATION
   ├─ Security Scanner checks for vulnerabilities
   ├─ Code Quality Validator checks style
   └─ Generate validation report

5. OUTPUT
   └─ Complete project structure ready for development
```

### Context Flow Between Agents

```
BackendAgent Output (APIs, DB Schema)
    ↓ (via previous_artifacts)
    └→ FrontendAgent (knows API endpoints)
    └→ TestingAgent (knows API signatures)

FrontendAgent Output (Component Signatures)
    ↓ (via previous_artifacts)
    └→ TestingAgent (knows component props)

BackendAgent + FrontendAgent Output
    ↓ (via previous_artifacts)
    └→ DevOpsAgent (knows dependencies)
    └→ TestingAgent (knows deployment targets)
```

---

## System Prompts (Context for Each Agent)

Each agent is initialized with a system prompt. Store these in `prompts/system_prompts.json`:

```json
{
  "backend_agent": "You are a senior backend engineer with 10+ years of experience...",
  "frontend_agent": "You are a senior frontend engineer specializing in React/Next.js...",
  "devops_agent": "You are a DevOps engineer responsible for reliable infrastructure...",
  "testing_agent": "You are a QA engineer ensuring code correctness and reliability..."
}
```

---

## Integration Checklist for Your Custom Agents

When you develop your custom fine-tuned agents, ensure they:

### Input Validation
- [ ] Accept `AgentContext` parameter
- [ ] Validate all required fields in context
- [ ] Handle missing optional fields gracefully

### Output Format
- [ ] Return `AgentResult` object
- [ ] Populate `success`, `outputs`, `artifacts` fields
- [ ] Include metadata about generated code
- [ ] List all dependencies

### Code Quality
- [ ] No hardcoded secrets
- [ ] No debug print statements
- [ ] Proper error messages
- [ ] Consistent code style
- [ ] Type hints on all functions

### Integration with System
- [ ] Inherit from `BaseAgent`
- [ ] Implement `async perform()` method
- [ ] Work with async/await pattern
- [ ] Respect timeout_seconds in config
- [ ] Return structured artifacts

### Testing
- [ ] Create unit tests for agent logic
- [ ] Test with different contexts
- [ ] Verify artifact structure
- [ ] Test error handling

---

## File Submission Format

When you return your custom agents, submit them as:

```
agents/
├── __init__.py (updated exports)
├── base_agent.py (unchanged - keep existing)
├── specialist_agents.py (your custom agents)
└── custom_agents.py (optional - additional agents)
```

**Required Changes to Files:**
1. Update `agents/__init__.py` imports
2. Ensure all agents in `specialist_agents.py` inherit from `BaseAgent`
3. Update `llms/manager.py` if you add new system prompts

---

## Example: How to Test Your Agents Locally

```python
import asyncio
from agents import BackendAgent, AgentContext

async def test_backend_agent():
    agent = BackendAgent()
    
    context = AgentContext(
        project_name="Test App",
        project_description="Simple CRUD app",
        requirements=["REST API", "Authentication"],
        tech_stack={"backend": "fastapi", "database": "postgresql"},
        constraints=["Production-ready"],
        task_description="Create user authentication system"
    )
    
    result = await agent.run("Create JWT auth system", context)
    
    assert result.success
    assert "files" in result.artifacts
    assert len(result.outputs) > 0
    print("Agent test passed!")

asyncio.run(test_backend_agent())
```

---

## Next Steps for You

1. **Development Environment Setup**
   - Clone your project with your custom agents
   - Install dependencies: `pip install -r requirements.txt`
   - Create your agent implementations

2. **Implementation**
   - Implement each agent's `perform()` method
   - Follow the specifications above
   - Test locally before submitting

3. **Submission**
   - Push agents to a branch
   - Ensure all tests pass
   - Provide usage documentation

4. **Integration**
   - We integrate into main
   - Run end-to-end tests
   - Deploy to production

---

**This specification is your blueprint. All agents must comply with this contract for seamless integration.**

Last updated: December 23, 2025
Status: Ready for Custom Agent Development
