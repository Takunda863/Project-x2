#!/bin/bash
# Test script for MVP Factory components

set -e

echo "🧪 Testing MVP Factory Components"
echo "================================="

# Test task parser
echo ""
echo "1. Testing Task Parser..."
python -c "
from orchestrator.task_parser import parse_project_description
import json

example = 'Create a blogging platform with user authentication, markdown support, and comments'
result = parse_project_description(example)
print('Task Parser Result:')
print(f'  Tasks parsed: {len(result[\"parsed_tasks\"])}')
print(f'  Estimated time: {result[\"time_estimate\"][\"estimated_minutes\"]} minutes')
print(f'  Agents required: {result[\"agents_required\"]}')
"

# Test validation framework
echo ""
echo "2. Testing Validation Framework..."
python -c "
from validation.validator import validate_code_snippet
from validation.security_scanner import scan_for_security_vulnerabilities
import json

test_code = '''
def insecure_example():
    api_key = \"hardcoded-key\"
    query = \"SELECT * FROM users WHERE id = \" + user_input
    return query
'''

# Code quality validation
val_result = validate_code_snippet(test_code, 'python')
print('Code Validation:')
print(f'  Passed: {val_result[\"summary\"][\"passed\"]}')
print(f'  Checks: {val_result[\"summary\"][\"total_checks\"]}')

# Security scan
sec_result = scan_for_security_vulnerabilities('test.py', test_code)
print('Security Scan:')
print(f'  Vulnerabilities found: {sec_result[\"vulnerabilities_found\"]}')
print(f'  Risk level: {sec_result[\"security_report\"][\"risk_level\"]}')
"

# Test agent stubs
echo ""
echo "3. Testing Agent Stubs..."
python -c "
from agents.specialist_agents import AgentFactory, AgentRole
from agents.base_agent import AgentConfig

config = AgentConfig(
    llm_provider='mock',
    llm_model='mock-model',
    temperature=0.1,
    max_tokens=1000
)

# Create agents
backend_agent = AgentFactory.create_agent(AgentRole.BACKEND_ENGINEER, config)
frontend_agent = AgentFactory.create_agent(AgentRole.FRONTEND_ENGINEER, config)

print('Agents Created:')
print(f'  Backend Agent: {backend_agent.name}')
print(f'    Role: {backend_agent.role}')
print(f'    Capabilities: {backend_agent.capabilities}')

print(f'  Frontend Agent: {frontend_agent.name}')
print(f'    Role: {frontend_agent.role}')
print(f'    Capabilities: {frontend_agent.capabilities}')
"

# Test orchestrator skeleton
echo ""
echo "4. Testing Orchestrator Skeleton..."
python -c "
from orchestrator.master_orchestrator import MasterOrchestrator
import asyncio

async def test_orchestrator():
    orchestrator = MasterOrchestrator()
    print('Orchestrator initialized:')
    print(f'  Has task parser: {hasattr(orchestrator, \"task_parser\")}')
    print(f'  Has agent factory: {hasattr(orchestrator, \"agent_factory\")}')
    
    # Note: Full execution requires LLM integration
    print('  Status: Ready for integration with LLM')

asyncio.run(test_orchestrator())
"

echo ""
echo "✅ Component testing completed!"
echo ""
echo "Next steps:"
echo "1. Run unit tests: pytest tests/"
echo "2. Run CI workflow checks"
echo "3. Integrate with LLM provider"
echo "4. Fine-tune models for specific roles"
