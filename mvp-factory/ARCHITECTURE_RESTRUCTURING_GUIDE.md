# 🏗️ Architecture Restructuring Guide

## Part 1: Yes, You Can Completely Restructure

The MVP Factory architecture is **fully modular and restructurable**. No components are locked in.

---

## Current Architecture (Can Be Changed)

```
MasterOrchestrator (main entry point)
    ↓
TaskParser (parse NL to tasks)
    ↓
┌─────────────────────────────────────┐
│ Parallel Agent Execution            │
├─────────────────────────────────────┤
│ BackendAgent    FrontendAgent       │
│ DevOpsAgent     TestingAgent        │
└─────────────────────────────────────┘
    ↓
ValidationEngine
    ↓
Artifact Assembly
```

---

## Architecture Options You Can Implement

### Option 1: Sequential Pipeline (Recommended for Dependencies)

```python
# orchestrator/sequential_orchestrator.py

class SequentialOrchestrator:
    """Execute agents in sequence, each gets output from previous"""
    
    async def orchestrate(self, description: str, tech_stack: Dict) -> Dict:
        # Phase 1: Parse and plan
        tasks = await self.parse_tasks(description)
        
        # Phase 2: Backend creates API spec
        backend_result = await self.backend_agent.run(
            task="Create REST API",
            context=AgentContext(...)
        )
        
        # Phase 3: Frontend uses API spec
        frontend_result = await self.frontend_agent.run(
            task="Create UI components",
            context=AgentContext(
                ...
                previous_artifacts=backend_result.artifacts  # ← Uses Phase 2 output
            )
        )
        
        # Phase 4: DevOps uses both outputs
        devops_result = await self.devops_agent.run(
            task="Setup infrastructure",
            context=AgentContext(
                ...
                previous_artifacts={
                    "backend": backend_result.artifacts,
                    "frontend": frontend_result.artifacts
                }
            )
        )
        
        # Phase 5: Testing validates everything
        testing_result = await self.testing_agent.run(
            task="Create test suite",
            context=AgentContext(
                ...
                previous_artifacts={
                    "backend": backend_result.artifacts,
                    "frontend": frontend_result.artifacts,
                    "devops": devops_result.artifacts
                }
            )
        )
        
        return self.assemble_final_project({
            "backend": backend_result,
            "frontend": frontend_result,
            "devops": devops_result,
            "testing": testing_result
        })
```

**Advantages:**
- ✅ Clear dependencies
- ✅ Each phase builds on previous
- ✅ Simpler debugging
- ✅ Natural workflow

**Disadvantages:**
- ❌ Slower (sequential, not parallel)
- ❌ If one fails, rest fail

---

### Option 2: Phase-Based Orchestration (Best of Both)

```python
# orchestrator/phase_orchestrator.py

class PhaseOrchestrator:
    """Execute agents in phases, parallel within phase"""
    
    async def orchestrate(self, description: str, tech_stack: Dict) -> Dict:
        tasks = await self.parse_tasks(description)
        
        # Phase 1: Parallel (no dependencies)
        phase1_results = await asyncio.gather(
            self.backend_agent.run("Create API", context),
            self.devops_agent.run("Plan infrastructure", context),
            return_exceptions=True
        )
        backend_result, devops_result = phase1_results
        
        # Phase 2: Parallel (depends on Phase 1)
        phase2_results = await asyncio.gather(
            self.frontend_agent.run("Create UI", AgentContext(..., 
                previous_artifacts=backend_result.artifacts
            )),
            self.testing_agent.run("Plan tests", AgentContext(...,
                previous_artifacts={
                    "backend": backend_result.artifacts,
                    "devops": devops_result.artifacts
                }
            )),
            return_exceptions=True
        )
        frontend_result, testing_result = phase2_results
        
        # Final assembly
        return self.assemble({
            "backend": backend_result,
            "frontend": frontend_result,
            "devops": devops_result,
            "testing": testing_result
        })
```

**Advantages:**
- ✅ Uses parallelization where possible
- ✅ Respects dependencies
- ✅ Good performance
- ✅ Clear phase structure

---

### Option 3: DAG-Based (Most Flexible)

```python
# orchestrator/dag_orchestrator.py

from dataclasses import dataclass
import networkx as nx

@dataclass
class ExecutionDAG:
    """Directed Acyclic Graph for execution"""
    graph: nx.DiGraph
    agents: Dict[str, BaseAgent]

class DAGOrchestrator:
    """Execute based on dependency graph"""
    
    async def orchestrate(self, description: str, tech_stack: Dict) -> Dict:
        # Build execution graph
        dag = self.build_execution_dag(description)
        
        # Execute in topological order
        results = {}
        for node in nx.topological_sort(dag.graph):
            agent = dag.agents[node]
            dependencies = list(dag.graph.predecessors(node))
            
            # Get data from dependencies
            dep_artifacts = {dep: results[dep].artifacts for dep in dependencies}
            
            # Execute agent
            result = await agent.run(
                task=dag.graph.nodes[node]['task'],
                context=AgentContext(..., previous_artifacts=dep_artifacts)
            )
            results[node] = result
        
        return self.assemble(results)
    
    def build_execution_dag(self, description: str) -> ExecutionDAG:
        """Build execution graph from description"""
        graph = nx.DiGraph()
        
        # Define nodes
        graph.add_node("backend", task="Create API", agent="backend_agent")
        graph.add_node("frontend", task="Create UI", agent="frontend_agent")
        graph.add_node("devops", task="Setup infra", agent="devops_agent")
        graph.add_node("testing", task="Create tests", agent="testing_agent")
        
        # Define edges (dependencies)
        graph.add_edge("backend", "frontend")    # Frontend depends on Backend
        graph.add_edge("backend", "testing")     # Testing depends on Backend
        graph.add_edge("frontend", "testing")    # Testing depends on Frontend
        graph.add_edge("devops", "testing")      # Testing depends on DevOps
        
        # Could also be dynamic based on description
        # Custom agents, custom dependencies, etc.
        
        return ExecutionDAG(graph, self.agents)
```

**Advantages:**
- ✅ Most flexible
- ✅ Custom dependencies
- ✅ Easy to extend
- ✅ Visual debugging possible

**Disadvantages:**
- ❌ More complex to implement
- ❌ Overkill for simple cases

---

### Option 4: Event-Driven (Most Scalable)

```python
# orchestrator/event_orchestrator.py

from dataclasses import dataclass
from typing import Callable
import asyncio

@dataclass
class AgentEvent:
    agent_id: str
    event_type: str  # "started", "completed", "failed"
    result: Optional[AgentResult] = None

class EventDrivenOrchestrator:
    """Agents publish events, orchestrator reacts"""
    
    def __init__(self):
        self.event_queue = asyncio.Queue()
        self.agents = {}
        self.event_handlers = {}
    
    def on_event(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def orchestrate(self, description: str, tech_stack: Dict) -> Dict:
        # Setup event handlers
        self.on_event("backend_completed", self.on_backend_ready)
        self.on_event("frontend_completed", self.on_frontend_ready)
        self.on_event("devops_completed", self.on_devops_ready)
        
        # Start all agents (they'll wait for dependencies)
        await asyncio.gather(
            self.backend_agent.run_async(description),
            self.frontend_agent.run_async(description),
            self.devops_agent.run_async(description),
            self.testing_agent.run_async(description),
            return_exceptions=True
        )
        
        return await self.assemble_results()
    
    async def on_backend_ready(self, event: AgentEvent):
        """Backend finished, notify dependent agents"""
        self.results["backend"] = event.result
        
        # Trigger frontend and testing
        await self.event_queue.put(AgentEvent(
            agent_id="frontend",
            event_type="dependency_ready"
        ))
        await self.event_queue.put(AgentEvent(
            agent_id="testing",
            event_type="backend_ready"
        ))
```

**Advantages:**
- ✅ Most scalable
- ✅ Great for microservices
- ✅ Decoupled agents
- ✅ Easy to monitor

---

### Option 5: Custom Distributed Execution

```python
# orchestrator/distributed_orchestrator.py

class WorkerPool:
    """Manage pool of agent workers"""
    
    def __init__(self, num_workers: int = 4):
        self.workers = [AgentWorker(i) for i in range(num_workers)]
        self.task_queue = asyncio.Queue()
        self.result_storage = {}

class AgentWorker:
    """Individual worker that executes tasks"""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.current_task = None
    
    async def work(self):
        """Process tasks from queue"""
        while True:
            task = await self.task_queue.get()
            if task is None:
                break
            
            self.current_task = task
            result = await task.agent.run(task.description, task.context)
            await self.result_storage.put(result)

class DistributedOrchestrator:
    """Distribute agent execution across worker pool"""
    
    async def orchestrate(self, description: str, tech_stack: Dict) -> Dict:
        pool = WorkerPool(num_workers=4)
        
        # Queue all tasks
        for agent in self.agents:
            await pool.task_queue.put(Task(
                agent=agent,
                description=description,
                context=AgentContext(...)
            ))
        
        # Run workers
        results = await asyncio.gather(*[w.work() for w in pool.workers])
        
        return self.assemble(results)
```

---

## How to Implement Your Restructuring

### Step 1: Choose Architecture
- Option 1: Sequential (simple, dependent tasks)
- Option 2: Phase-based (recommended)
- Option 3: DAG-based (flexible)
- Option 4: Event-driven (scalable)
- Option 5: Custom distributed (advanced)

### Step 2: Create New Orchestrator

```python
# orchestrator/your_orchestrator.py

class YourCustomOrchestrator:
    """Your new orchestration logic"""
    
    def __init__(self):
        self.backend_agent = BackendAgent()
        self.frontend_agent = FrontendAgent()
        self.devops_agent = DevOpsAgent()
        self.testing_agent = TestingAgent()
    
    async def orchestrate(self, description: str, tech_stack: Dict) -> Dict:
        # YOUR execution logic here
        # No constraints - you control everything
        pass
```

### Step 3: Update Entry Point

```python
# main.py or entry point

# Old
# from orchestrator.master_orchestrator import create_mvp
# result = await create_mvp(...)

# New
from orchestrator.your_orchestrator import YourCustomOrchestrator

orchestrator = YourCustomOrchestrator()
result = await orchestrator.orchestrate(description, tech_stack)
```

### Step 4: Update Tests

```python
# tests/test_custom_orchestrator.py

@pytest.mark.asyncio
async def test_custom_orchestration():
    orchestrator = YourCustomOrchestrator()
    result = await orchestrator.orchestrate(
        description="Test project",
        tech_stack={"backend": "fastapi"}
    )
    assert result["success"]
```

---

## Migration Path (Zero Breaking Changes)

### Phase 1: New Orchestrator Coexists
```python
# Both available
from orchestrator.master_orchestrator import MasterOrchestrator  # Old
from orchestrator.your_orchestrator import YourOrchestrator      # New

# Choose which to use
orchestrator = YourOrchestrator()  # Use new
```

### Phase 2: Transition
```python
# Gradually move code to new orchestrator
# BaseAgent, system prompts, agents all still work
# Just different execution logic
```

### Phase 3: Deprecate Old (Optional)
```python
# Can keep both or remove old one
# Agents and everything else unchanged
```

---

## Key Flexibility Points

| Component | Can Change? | How |
|-----------|-------------|-----|
| Execution order | ✅ YES | Your orchestrator controls |
| Agent selection | ✅ YES | Load different agents |
| Data flow | ✅ YES | Pass different context |
| Parallelization | ✅ YES | Use asyncio as needed |
| Error handling | ✅ YES | Your error logic |
| Result assembly | ✅ YES | Your assembly logic |
| Validation pipeline | ✅ YES | Call at different point |
| Task parsing | ✅ YES | Use different parser |

---

## What DOESN'T Change

These stay the same regardless of orchestration:

- ✅ BaseAgent interface (all agents still inherit from it)
- ✅ System prompts (still loaded per role)
- ✅ AgentResult format (output stays same)
- ✅ Agent implementations (BackendAgent, etc. unchanged)
- ✅ LLM integration (call_llm still works)
- ✅ Validation framework (still available)

---

## Recommendation

**For your custom fine-tuned agents, I recommend: Option 2 (Phase-Based)**

```python
# orchestrator/phase_orchestrator.py

class PhaseOrchestrator:
    """Phase-based execution with parallelization"""
    
    async def orchestrate(self, description: str, tech_stack: Dict) -> Dict:
        
        # Phase 1: Independent agents (parallel)
        phase1 = await asyncio.gather(
            self.backend_agent.run(...),
            self.devops_agent.run(...)
        )
        
        # Phase 2: Dependent agents (parallel, use Phase 1 output)
        phase2 = await asyncio.gather(
            self.frontend_agent.run(..., previous_artifacts=phase1[0].artifacts),
            self.testing_agent.run(..., previous_artifacts=...)
        )
        
        return self.assemble(phase1 + phase2)
```

**Why?**
- ✅ Clear, understandable structure
- ✅ Good performance (parallelization)
- ✅ Respects dependencies
- ✅ Easy to debug
- ✅ Easy to extend with new agents
- ✅ Perfect for custom fine-tuned agents

---

## Summary

✅ **You can completely restructure the architecture**
- No components are locked in
- Choose your orchestration strategy
- All agent code stays the same
- Zero breaking changes to agents/prompts

✅ **Combined with Instruction Isolation**
- Each agent gets only its prompt (see INSTRUCTION_ISOLATION_GUIDE.md)
- No cross-agent information leakage
- Clean, modular, secure system

**You have complete architectural freedom! 🚀**
