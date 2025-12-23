"""
Tests for the Validation Framework
"""

import pytest
import json
from validation.validator import ValidationEngine, validate_code_snippet
from validation.security_scanner import scan_for_security_vulnerabilities, detect_llm_generated_code

def test_validation_engine_initialization():
    """Test ValidationEngine initialization"""
    engine = ValidationEngine()
    assert engine is not None
    assert hasattr(engine, 'validators')
    assert 'security' in engine.validators
    assert 'code_quality' in engine.validators

def test_validate_code_snippet():
    """Test code snippet validation"""
    test_code = """
def example():
    return "Hello World"
"""
    
    result = validate_code_snippet(test_code, "python")
    
    assert 'snippet_length' in result
    assert 'language' in result
    assert 'summary' in result
    assert 'results' in result
    
    # Clean code should pass
    assert result['summary']['passed'] == True

def test_security_vulnerability_detection():
    """Test security vulnerability scanning"""
    vulnerable_code = """
def insecure():
    api_key = "hardcoded-key-12345"
    query = "SELECT * FROM users WHERE id = " + user_input
    return execute(query)
"""
    
    result = scan_for_security_vulnerabilities("test.py", vulnerable_code)
    
    assert 'vulnerabilities_found' in result
    assert 'security_report' in result
    assert 'validation_results' in result
    
    # Should find at least one vulnerability
    assert result['vulnerabilities_found'] > 0

def test_llm_generated_code_detection():
    """Test LLM-generated code detection"""
    llm_like_code = """
def process_data(data):
    \"\"\"Process the input data.
    
    Args:
        data: The data to process
        
    Returns:
        Processed result
    \"\"\"
    try:
        # Important: Validate input first
        if not data:
            raise ValueError("Data cannot be empty")
        return data.upper()
    except Exception as e:
        print(f"Error processing data: {e}")
        return None
"""
    
    result = detect_llm_generated_code(llm_like_code)
    
    assert 'llm_score' in result
    assert 'likely_llm_generated' in result
    assert 'fingerprints_found' in result
    assert 'fingerprints' in result
    
    # LLM-like code should have higher score
    assert 0 <= result['llm_score'] <= 1

def test_validation_engine_full_project():
    """Test validation engine on multiple files"""
    engine = ValidationEngine()
    
    project_files = {
        "main.py": """
def main():
    print("Hello World")
    
if __name__ == "__main__":
    main()
""",
        "utils.js": """
function helper() {
    console.log("Helper function");
    return true;
}
"""
    }
    
    result = engine.validate_project(project_files)
    
    assert 'success' in result
    assert 'summary' in result
    assert 'detailed_results' in result
    assert 'total_files' in result
    assert 'total_checks' in result
    
    # Should have checked both files
    assert result['total_files'] == 2

def test_security_scanner_patterns():
    """Test security scanner pattern matching"""
    from validation.security_scanner import SecurityScanner
    
    scanner = SecurityScanner()
    
    # Test SQL injection pattern
    sql_injection_code = "query = 'SELECT * FROM users WHERE id = ' + user_id"
    results = scanner.scan_file("test.py", sql_injection_code)
    
    # Should find SQL injection vulnerability
    sql_vulns = [r for r in results if "SQL" in r.check_name]
    assert len(sql_vulns) > 0

@pytest.mark.parametrize("code,expected_vulnerabilities", [
    ("api_key = 'sk-12345'", 1),  # Hardcoded secret
    ("password = 'mypassword'", 1),  # Hardcoded password
    ("def safe(): return 1", 0),  # Safe code
])
def test_security_patterns(code, expected_vulnerabilities):
    """Test specific security patterns"""
    result = scan_for_security_vulnerabilities("test.py", code)
    assert result['vulnerabilities_found'] == expected_vulnerabilities

if __name__ == "__main__":
    # Run tests
    test_validation_engine_initialization()
    test_validate_code_snippet()
    test_security_vulnerability_detection()
    test_llm_generated_code_detection()
    test_validation_engine_full_project()
    test_security_scanner_patterns()
    print("✅ All validation tests passed!")
