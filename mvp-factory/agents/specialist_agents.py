"""
Specialist Agent Implementations
Concrete implementations of BaseAgent for different development roles
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

from .base_agent import BaseAgent, AgentResult, AgentConfig
from llms.manager import call_llm, LLMCallOptions

class AgentRole(Enum):
    """Specialized agent roles"""
    BACKEND_ENGINEER = "backend_engineer"
    FRONTEND_ENGINEER = "frontend_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    TESTING_ENGINEER = "testing_engineer"
    ML_ENGINEER = "ml_engineer"

@dataclass
class AgentContext:
    """Context information for agent execution"""
    project_name: str
    project_description: str
    requirements: List[str]
    tech_stack: Dict[str, str]
    constraints: List[str]
    previous_artifacts: Dict[str, Any] = None
    task_description: str = ""

class BackendAgent(BaseAgent):
    """
    Backend/API specialist agent
    Generates backend code, APIs, databases, and business logic
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        cfg = config or AgentConfig(name="backend_engineer", role="Backend Engineer")
        super().__init__(cfg)
        self.name = "BackendEngineer"
        self.role = "Design and implement backend APIs, databases, and business logic"
        self.capabilities = ["api_design", "database_schema", "business_logic", "authentication", "api_integration"]
        
    async def execute(self, task_description: str, context: AgentContext) -> AgentResult:
        """
        Execute a backend development task
        
        Args:
            task_description: Description of what to build
            context: Project context and requirements
            
        Returns:
            AgentResult with generated artifacts
        """
        try:
            # Prepare system prompt for backend engineering
            system_prompt = self._create_system_prompt(context)
            
            # Prepare user prompt with task details
            user_prompt = self._create_user_prompt(task_description, context)
            
            # Call LLM for code generation
            llm_response = call_llm(
                role="backend_agent",
                user_prompt=user_prompt,
                system_override=system_prompt,
                opts=LLMCallOptions(temperature=0.2, max_tokens=2048)
            )
            
            # Parse LLM response into structured artifacts
            artifacts = self._parse_llm_response(llm_response.get("text", ""))
            
            # Generate response
            return AgentResult(
                success=True,
                outputs=[llm_response.get("text", "")],
                artifacts=artifacts
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                outputs=[],
                artifacts={},
                error=f"Backend agent execution failed: {str(e)}"
            )
    
    def _create_system_prompt(self, context: AgentContext) -> str:
        """Create system prompt for backend agent"""
        tech_stack_str = json.dumps(context.tech_stack, indent=2)
        
        return f"""You are a senior backend engineer with 10+ years of experience.
You specialize in building scalable, secure, and maintainable backend systems.

Project Context:
- Project Name: {context.project_name}
- Tech Stack: {tech_stack_str}
- Requirements: {', '.join(context.requirements)}
- Constraints: {', '.join(context.constraints)}

Capabilities:
- API design (REST, GraphQL)
- Database schema design (SQL, NoSQL)
- Authentication/Authorization (JWT, OAuth)
- Business logic implementation
- Error handling and logging
- Performance optimization
- Security best practices

Output Format:
You MUST respond with a JSON object containing:
1. "architecture": High-level architecture description
2. "api_endpoints": List of API endpoints with methods, paths, and descriptions
3. "database_schema": Database schema design
4. "code_snippets": Key code implementations
5. "dependencies": Required packages/libraries
6. "environment_variables": Configuration variables needed
7. "testing_strategy": How to test this backend

Always include security considerations and error handling."""
    
    def _create_user_prompt(self, task_description: str, context: AgentContext) -> str:
        """Create user prompt for specific task"""
        return f"""Task: {task_description}

Please provide a complete backend implementation for this task.

Considerations:
1. Follow best practices for the tech stack: {json.dumps(context.tech_stack)}
2. Ensure security (input validation, authentication, etc.)
3. Make it production-ready with proper error handling
4. Include API documentation
5. Consider scalability

Provide the implementation in the specified JSON format."""
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured artifacts"""
        try:
            # Try to parse as JSON
            if llm_response.strip().startswith('{'):
                return json.loads(llm_response)
        except json.JSONDecodeError:
            pass
        
        # Fallback: extract code blocks and structure
        artifacts = {
            "architecture": "",
            "api_endpoints": [],
            "database_schema": {},
            "code_snippets": {},
            "dependencies": [],
            "environment_variables": {},
            "testing_strategy": ""
        }
        
        # Extract code blocks
        import re
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', llm_response, re.DOTALL)
        
        if code_blocks:
            artifacts["code_snippets"] = {
                f"code_block_{i}": block
                for i, block in enumerate(code_blocks)
            }
        
        return artifacts

class FrontendAgent(BaseAgent):
    """
    Frontend/UI specialist agent
    Generates user interfaces, components, and frontend logic
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        cfg = config or AgentConfig(name="frontend_engineer", role="Frontend Engineer")
        super().__init__(cfg)
        self.name = "FrontendEngineer"
        self.role = "Create responsive, accessible user interfaces with modern frameworks"
        self.capabilities = ["react", "vue", "nextjs", "tailwind", "component_design", "state_management"]
    
    async def execute(self, task_description: str, context: AgentContext) -> AgentResult:
        """Execute a frontend development task"""
        try:
            system_prompt = self._create_system_prompt(context)
            user_prompt = self._create_user_prompt(task_description, context)
            
            llm_response = call_llm(
                role="frontend_agent",
                user_prompt=user_prompt,
                system_override=system_prompt,
                opts=LLMCallOptions(temperature=0.2, max_tokens=2048)
            )
            
            artifacts = self._parse_llm_response(llm_response.get("text", ""))
            
            return AgentResult(
                success=True,
                outputs=[llm_response.get("text", "")],
                artifacts=artifacts
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                outputs=[],
                artifacts={},
                error=f"Frontend agent execution failed: {str(e)}"
            )
    
    def _create_system_prompt(self, context: AgentContext) -> str:
        framework = context.tech_stack.get("frontend", "react")
        
        return f"""You are a senior frontend engineer specializing in {framework.upper()}.
You create beautiful, responsive, and accessible user interfaces.

Project Context:
- Project: {context.project_name}
- Framework: {framework}
- Requirements: {', '.join(context.requirements)}
- Must be mobile-responsive and accessible (WCAG 2.1 AA)

Output Format:
Provide a JSON object with:
1. "component_structure": How components are organized
2. "ui_design": Design considerations and mockups
3. "code_components": Actual component code
4. "state_management": How state is handled
5. "routing": Page routing structure
6. "styling": CSS/Tailwind/Styled Components setup
7. "accessibility_features": Specific a11y implementations
8. "performance_optimizations": Loading, bundling, etc.

Focus on:
- User experience
- Performance (Lighthouse scores >90)
- Accessibility
- Maintainability
- Responsive design"""
    
    def _create_user_prompt(self, task_description: str, context: AgentContext) -> str:
        return f"""Task: {task_description}

Create a complete frontend implementation for this feature.

Requirements:
- Use {context.tech_stack.get('frontend', 'react')} framework
- Follow modern best practices
- Ensure excellent UX and accessibility
- Make it production-ready

Provide the complete implementation."""
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        # Similar parsing logic as BackendAgent
        try:
            if llm_response.strip().startswith('{'):
                return json.loads(llm_response)
        except:
            pass
        
        return {
            "components": [],
            "styles": {},
            "state_management": "",
            "code_blocks": self._extract_code_blocks(llm_response)
        }
    
    def _extract_code_blocks(self, text: str) -> Dict[str, str]:
        import re
        blocks = re.findall(r'```(?:jsx?|tsx?|javascript|typescript)?\n(.*?)\n```', text, re.DOTALL)
        return {f"component_{i}": block for i, block in enumerate(blocks)}

class DevOpsAgent(BaseAgent):
    """
    DevOps/Cloud specialist agent
    Generates infrastructure, CI/CD, and deployment configurations
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        cfg = config or AgentConfig(name="devops_engineer", role="DevOps Engineer")
        super().__init__(cfg)
        self.name = "DevOpsEngineer"
        self.role = "Set up deployment, CI/CD, infrastructure, and monitoring"
        self.capabilities = ["docker", "kubernetes", "aws", "ci_cd", "monitoring", "terraform"]
    
    async def execute(self, task_description: str, context: AgentContext) -> AgentResult:
        """Execute a DevOps/infrastructure task"""
        try:
            system_prompt = self._create_system_prompt(context)
            user_prompt = self._create_user_prompt(task_description, context)
            
            llm_response = call_llm(
                role="devops_agent",
                user_prompt=user_prompt,
                system_override=system_prompt,
                opts=LLMCallOptions(temperature=0.2, max_tokens=2048)
            )
            
            artifacts = self._parse_llm_response(llm_response.get("text", ""))
            
            return AgentResult(
                success=True,
                outputs=[llm_response.get("text", "")],
                artifacts=artifacts
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                outputs=[],
                artifacts={},
                error=f"DevOps agent execution failed: {str(e)}"
            )
    
    def _create_system_prompt(self, context: AgentContext) -> str:
        deployment = context.tech_stack.get("deployment", "vercel")
        
        return f"""You are a senior DevOps engineer specializing in {deployment.upper()}.
You design scalable, secure, and cost-effective infrastructure.

Project Context:
- Project: {context.project_name}
- Deployment Target: {deployment}
- Requirements: {', '.join(context.requirements)}
- Must be production-ready and secure

Output Format:
Provide a JSON object with:
1. "infrastructure": Infrastructure as Code (Terraform/CloudFormation)
2. "ci_cd_pipeline": CI/CD configuration (GitHub Actions, GitLab CI, etc.)
3. "docker_configuration": Dockerfiles and docker-compose
4. "monitoring_setup": Logging, metrics, alerts
5. "security_configuration": Security groups, IAM roles, etc.
6. "scaling_configuration": Auto-scaling, load balancing
7. "cost_estimation": Monthly cost estimate
8. "deployment_instructions": Step-by-step deployment guide

Focus on:
- Security best practices
- High availability
- Cost optimization
- Easy maintenance
- Disaster recovery"""
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        try:
            if llm_response.strip().startswith('{'):
                return json.loads(llm_response)
        except:
            pass
        
        return {
            "dockerfiles": {},
            "ci_cd_config": {},
            "infrastructure": {},
            "deployment_guide": ""
        }

class TestingAgent(BaseAgent):
    """
    Testing specialist agent
    Generates test suites, validation scripts, and quality checks
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        cfg = config or AgentConfig(name="testing_engineer", role="Testing Engineer")
        super().__init__(cfg)
        self.name = "TestingEngineer"
        self.role = "Create comprehensive test suites and validation frameworks"
        self.capabilities = ["unit_tests", "integration_tests", "e2e_tests", "load_tests", "security_tests"]
    
    async def execute(self, task_description: str, context: AgentContext) -> AgentResult:
        """Execute a testing/validation task"""
        try:
            system_prompt = self._create_system_prompt(context)
            user_prompt = self._create_user_prompt(task_description, context)
            
            llm_response = call_llm(
                role="testing_validation",
                user_prompt=user_prompt,
                system_override=system_prompt,
                opts=LLMCallOptions(temperature=0.2, max_tokens=2048)
            )
            
            artifacts = self._parse_llm_response(llm_response.get("text", ""))
            
            return AgentResult(
                success=True,
                outputs=[llm_response.get("text", "")],
                artifacts=artifacts
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                outputs=[],
                artifacts={},
                error=f"Testing agent execution failed: {str(e)}"
            )
    
    def _create_system_prompt(self, context: AgentContext) -> str:
        return f"""You are a senior testing engineer specializing in comprehensive test strategies.
You create maintainable, reliable test suites that ensure quality.

Project Context:
- Project: {context.project_name}
- Tech Stack: {json.dumps(context.tech_stack)}
- Requirements: {', '.join(context.requirements)}
- Must achieve high test coverage and reliability

Output Format:
Provide a JSON object with:
1. "test_strategy": Overall testing approach
2. "unit_tests": Unit test implementations
3. "integration_tests": Integration test implementations
4. "e2e_tests": End-to-end test implementations
5. "test_data": Test data generation and management
6. "ci_testing": CI pipeline test configuration
7. "coverage_report": Coverage setup and targets
8. "performance_tests": Load and performance testing
9. "security_tests": Security vulnerability testing

Focus on:
- Test maintainability
- Coverage of critical paths
- Fast test execution
- Reliability and flakiness prevention
- Realistic test data"""

class AgentFactory:
    """Factory for creating specialist agents"""
    
    @staticmethod
    def create_agent(role: AgentRole, config: Optional[AgentConfig] = None) -> BaseAgent:
        """Create a specialist agent by role"""
        config = config or AgentConfig()
        
        if role == AgentRole.BACKEND_ENGINEER:
            return BackendAgent(config)
        elif role == AgentRole.FRONTEND_ENGINEER:
            return FrontendAgent(config)
        elif role == AgentRole.DEVOPS_ENGINEER:
            return DevOpsAgent(config)
        elif role == AgentRole.TESTING_ENGINEER:
            return TestingAgent(config)
        else:
            raise ValueError(f"Unknown agent role: {role}")

# Example usage
async def example_agent_execution():
    """Example of how to use the specialist agents"""
    
    # Create context
    context = AgentContext(
        project_name="Task Manager",
        project_description="A collaborative task management application",
        requirements=["User authentication", "CRUD operations", "Real-time updates"],
        tech_stack={"backend": "fastapi", "frontend": "nextjs", "database": "postgresql"},
        constraints=["Deploy in 15 minutes", "Free tier services"]
    )
    
    # Create backend agent
    backend_agent = BackendAgent()
    
    # Execute task
    response = await backend_agent.execute(
        "Create user authentication API",
        context
    )
    
    if response.success:
        print("Backend agent executed successfully!")
        print(f"Generated artifacts: {len(response.artifacts)}")
    else:
        print(f"Backend agent failed: {response.errors}")

if __name__ == "__main__":
    # Run example
    asyncio.run(example_agent_execution())
