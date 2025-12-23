"""
Task Parser Module
Converts natural language project descriptions into structured tasks
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    """Types of development tasks"""
    CREATE_API = "create_api"
    CREATE_UI = "create_ui"
    SETUP_DATABASE = "setup_database"
    IMPLEMENT_AUTH = "implement_auth"
    ADD_FEATURE = "add_feature"
    DEPLOY = "deploy"
    TEST = "test"
    INTEGRATE_SERVICE = "integrate_service"

@dataclass
class Task:
    """Structured development task"""
    task_id: str
    task_type: TaskType
    description: str
    priority: int  # 1=highest, 3=lowest
    dependencies: List[str]  # task_ids this depends on
    estimated_time: int  # in minutes
    agent_type: str  # which agent should handle this
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "description": self.description,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "estimated_time": self.estimated_time,
            "agent_type": self.agent_type,
            "parameters": self.parameters
        }

class TaskParser:
    """
    Parses natural language project descriptions into structured task lists
    Can be extended with LLM-based parsing later
    """
    
    def __init__(self):
        # Common patterns for rule-based parsing
        self.patterns = {
            "auth": [
                r"user.*(auth|login|sign.?in|sign.?up|register)",
                r"authenticat",
                r"jwt|oauth|saml"
            ],
            "api": [
                r"(api|endpoint|rest|graphql)",
                r"(get|post|put|delete).*data",
                r"crud|create.*read.*update.*delete"
            ],
            "database": [
                r"database|db|store.*data",
                r"postgres|mysql|mongodb|sqlite",
                r"schema|table|collection"
            ],
            "ui": [
                r"ui|ux|interface|front.?end",
                r"page|screen|view",
                r"react|vue|angular|svelte"
            ],
            "deploy": [
                r"deploy|host|publish",
                r"server|cloud|aws|azure|gcp",
                r"docker|container|kubernetes"
            ]
        }
        
        # Agent mapping
        self.agent_mapping = {
            "auth": "auth_agent",
            "api": "backend_agent", 
            "database": "backend_agent",
            "ui": "frontend_agent",
            "deploy": "devops_agent"
        }
    
    def parse_natural_language(self, description: str) -> List[Task]:
        """
        Parse natural language description into tasks
        This is a rule-based implementation that can be replaced with LLM
        """
        description_lower = description.lower()
        
        # Extract requirements using simple pattern matching
        tasks = []
        task_id_counter = 1
        
        # Check for authentication requirements
        if any(re.search(pattern, description_lower) for pattern in self.patterns["auth"]):
            tasks.append(Task(
                task_id=f"TASK_{task_id_counter:03d}",
                task_type=TaskType.IMPLEMENT_AUTH,
                description="Implement user authentication system",
                priority=1,
                dependencies=[],
                estimated_time=30,
                agent_type=self.agent_mapping.get("auth", "backend_agent"),
                parameters={
                    "auth_method": "jwt",
                    "features": ["login", "register", "password_reset"]
                }
            ))
            task_id_counter += 1
        
        # Check for API requirements
        if any(re.search(pattern, description_lower) for pattern in self.patterns["api"]):
            tasks.append(Task(
                task_id=f"TASK_{task_id_counter:03d}",
                task_type=TaskType.CREATE_API,
                description="Create REST API endpoints",
                priority=1,
                dependencies=["TASK_001"] if "TASK_001" in [t.task_id for t in tasks] else [],
                estimated_time=45,
                agent_type=self.agent_mapping.get("api", "backend_agent"),
                parameters={
                    "framework": "fastapi",
                    "documentation": True,
                    "versioning": "v1"
                }
            ))
            task_id_counter += 1
        
        # Check for database requirements
        if any(re.search(pattern, description_lower) for pattern in self.patterns["database"]):
            tasks.append(Task(
                task_id=f"TASK_{task_id_counter:03d}",
                task_type=TaskType.SETUP_DATABASE,
                description="Set up database schema and connection",
                priority=1,
                dependencies=[],
                estimated_time=25,
                agent_type=self.agent_mapping.get("database", "backend_agent"),
                parameters={
                    "database_type": "postgresql",
                    "orm": "sqlalchemy"
                }
            ))
            task_id_counter += 1
        
        # Check for UI requirements
        if any(re.search(pattern, description_lower) for pattern in self.patterns["ui"]):
            tasks.append(Task(
                task_id=f"TASK_{task_id_counter:03d}",
                task_type=TaskType.CREATE_UI,
                description="Create user interface components",
                priority=2,
                dependencies=[],
                estimated_time=40,
                agent_type=self.agent_mapping.get("ui", "frontend_agent"),
                parameters={
                    "framework": "nextjs",
                    "styling": "tailwind",
                    "responsive": True
                }
            ))
            task_id_counter += 1
        
        # Check for deployment requirements
        if any(re.search(pattern, description_lower) for pattern in self.patterns["deploy"]):
            tasks.append(Task(
                task_id=f"TASK_{task_id_counter:03d}",
                task_type=TaskType.DEPLOY,
                description="Set up deployment and CI/CD pipeline",
                priority=3,
                dependencies=[t.task_id for t in tasks if t.agent_type in ["backend_agent", "frontend_agent"]],
                estimated_time=35,
                agent_type=self.agent_mapping.get("deploy", "devops_agent"),
                parameters={
                    "platform": "vercel",
                    "ci_cd": "github_actions",
                    "containerize": True
                }
            ))
            task_id_counter += 1
        
        # Always add testing task
        tasks.append(Task(
            task_id=f"TASK_{task_id_counter:03d}",
            task_type=TaskType.TEST,
            description="Create test suite and validation",
            priority=2,
            dependencies=[t.task_id for t in tasks],
            estimated_time=20,
            agent_type=self.agent_mapping.get("testing", "testing_agent"),
            parameters={
                "test_types": ["unit", "integration"],
                "coverage_target": 80
            }
        ))
        
        return tasks
    
    def create_task_graph(self, tasks: List[Task]) -> Dict[str, Any]:
        """Create a dependency graph from tasks"""
        graph = {
            "nodes": [],
            "edges": [],
            "critical_path": []
        }
        
        for task in tasks:
            graph["nodes"].append({
                "id": task.task_id,
                "label": task.description,
                "type": task.task_type.value,
                "agent": task.agent_type,
                "priority": task.priority,
                "estimated_time": task.estimated_time
            })
            
            for dep in task.dependencies:
                graph["edges"].append({
                    "from": dep,
                    "to": task.task_id,
                    "type": "dependency"
                })
        
        return graph
    
    def estimate_total_time(self, tasks: List[Task]) -> Dict[str, Any]:
        """Estimate total development time based on task dependencies"""
        # Simple estimation: sum of max parallel branch times
        agent_tasks = {}
        for task in tasks:
            if task.agent_type not in agent_tasks:
                agent_tasks[task.agent_type] = []
            agent_tasks[task.agent_type].append(task)
        
        # Calculate parallel time (agents work concurrently)
        parallel_times = []
        for agent, agent_task_list in agent_tasks.items():
            agent_time = sum(t.estimated_time for t in agent_task_list)
            parallel_times.append(agent_time)
        
        # Total time is max of parallel chains + sequential dependency overhead
        estimated_total = max(parallel_times) if parallel_times else 0
        estimated_total = min(estimated_total * 1.2, 240)  # Add 20% buffer, cap at 4 hours
        
        return {
            "estimated_minutes": int(estimated_total),
            "parallel_agents": len(agent_tasks),
            "total_tasks": len(tasks),
            "breakdown": {agent: sum(t.estimated_time for t in tasks) 
                         for agent, tasks in agent_tasks.items()}
        }

def parse_project_description(description: str) -> Dict[str, Any]:
    """Convenience function to parse project description"""
    parser = TaskParser()
    tasks = parser.parse_natural_language(description)
    task_graph = parser.create_task_graph(tasks)
    time_estimate = parser.estimate_total_time(tasks)
    
    return {
        "success": True,
        "original_description": description,
        "parsed_tasks": [task.to_dict() for task in tasks],
        "task_graph": task_graph,
        "time_estimate": time_estimate,
        "agents_required": list(set(task.agent_type for task in tasks))
    }

if __name__ == "__main__":
    # Example usage
    example_description = """
    I need a task management app with user authentication, 
    a REST API for CRUD operations on tasks, 
    a React frontend with a clean UI, 
    and deployment to Vercel.
    """
    
    result = parse_project_description(example_description)
    print(json.dumps(result, indent=2))
