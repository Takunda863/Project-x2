"""
Tests for the Task Parser module
"""

import pytest
import json
from orchestrator.task_parser import TaskParser, parse_project_description

def test_task_parser_initialization():
    """Test TaskParser initialization"""
    parser = TaskParser()
    assert parser is not None
    assert hasattr(parser, 'patterns')
    assert 'auth' in parser.patterns

def test_parse_natural_language():
    """Test parsing natural language descriptions"""
    parser = TaskParser()
    
    # Test with authentication requirement
    description = "Create a web app with user login and registration"
    tasks = parser.parse_natural_language(description)
    
    assert len(tasks) > 0
    assert any('auth' in task.agent_type for task in tasks)

def test_parse_project_description_function():
    """Test the convenience function"""
    description = "Build a task manager with database and API"
    result = parse_project_description(description)
    
    assert result['success'] == True
    assert 'parsed_tasks' in result
    assert 'task_graph' in result
    assert 'time_estimate' in result
    
    # Verify structure
    assert isinstance(result['parsed_tasks'], list)
    assert isinstance(result['time_estimate'], dict)
    assert 'estimated_minutes' in result['time_estimate']

def test_task_graph_creation():
    """Test task graph creation"""
    parser = TaskParser()
    description = "App with auth and database"
    tasks = parser.parse_natural_language(description)
    graph = parser.create_task_graph(tasks)
    
    assert 'nodes' in graph
    assert 'edges' in graph
    assert 'critical_path' in graph
    
    # Should have nodes for each task
    assert len(graph['nodes']) == len(tasks)

def test_time_estimation():
    """Test time estimation logic"""
    parser = TaskParser()
    description = "Simple app with frontend and backend"
    tasks = parser.parse_natural_language(description)
    time_estimate = parser.estimate_total_time(tasks)
    
    assert 'estimated_minutes' in time_estimate
    assert 'parallel_agents' in time_estimate
    assert 'total_tasks' in time_estimate
    
    # Time should be reasonable (not negative, not extremely long)
    assert 0 < time_estimate['estimated_minutes'] < 240  # Less than 4 hours

@pytest.mark.parametrize("description,expected_tasks", [
    ("App with user authentication", 1),
    ("API with database", 1),
    ("Full stack app with UI and deployment", 3),
])
def test_different_descriptions(description, expected_tasks):
    """Test parser with different descriptions"""
    parser = TaskParser()
    tasks = parser.parse_natural_language(description)
    
    # Should have at least expected number of tasks
    assert len(tasks) >= expected_tasks
    
    # Each task should have required fields
    for task in tasks:
        assert hasattr(task, 'task_id')
        assert hasattr(task, 'task_type')
        assert hasattr(task, 'description')
        assert hasattr(task, 'priority')
        assert hasattr(task, 'dependencies')
        assert hasattr(task, 'estimated_time')
        assert hasattr(task, 'agent_type')
        assert hasattr(task, 'parameters')

if __name__ == "__main__":
    # Run tests
    test_task_parser_initialization()
    test_parse_natural_language()
    test_parse_project_description_function()
    test_task_graph_creation()
    test_time_estimation()
    print("✅ All task parser tests passed!")
