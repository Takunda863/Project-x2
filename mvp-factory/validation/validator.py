"""
Validation Framework
Validates generated code and artifacts for quality and security
"""

import ast
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import subprocess
import tempfile
import os

class ValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ValidationType(Enum):
    """Types of validations"""
    SECURITY = "security"
    CODE_QUALITY = "code_quality"
    PERFORMANCE = "performance"
    BEST_PRACTICE = "best_practice"
    SYNTAX = "syntax"
    CONFIGURATION = "configuration"

@dataclass
class ValidationResult:
    """Result of a validation check"""
    check_id: str
    check_name: str
    validation_type: ValidationType
    level: ValidationLevel
    passed: bool
    message: str
    details: Dict[str, Any]
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "check_id": self.check_id,
            "check_name": self.check_name,
            "validation_type": self.validation_type.value,
            "level": self.level.value,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "suggestion": self.suggestion
        }

class BaseValidator:
    """Base class for all validators"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def validate(self, content: str, file_path: Optional[str] = None) -> List[ValidationResult]:
        """Validate content - to be implemented by subclasses"""
        raise NotImplementedError
    
    def add_result(self, result: ValidationResult):
        """Add validation result"""
        self.results.append(result)
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get all results as dictionaries"""
        return [r.to_dict() for r in self.results]

class SecurityValidator(BaseValidator):
    """Validates security aspects of code"""
    
    def validate(self, content: str, file_path: Optional[str] = None) -> List[ValidationResult]:
        self.results = []
        
        # Check for hardcoded secrets
        self._check_hardcoded_secrets(content, file_path)
        
        # Check for SQL injection patterns
        self._check_sql_injection(content, file_path)
        
        # Check for XSS vulnerabilities
        self._check_xss_vulnerabilities(content, file_path)
        
        # Check for insecure dependencies
        self._check_insecure_dependencies(content, file_path)
        
        return self.results
    
    def _check_hardcoded_secrets(self, content: str, file_path: str):
        """Check for hardcoded API keys, passwords, etc."""
        secret_patterns = [
            (r'api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', "Hardcoded API key"),
            (r'password\s*[=:]\s*["\']([^"\']+)["\']', "Hardcoded password"),
            (r'secret[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', "Hardcoded secret key"),
            (r'token\s*[=:]\s*["\']([^"\']+)["\']', "Hardcoded token"),
        ]
        
        for pattern, description in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                self.add_result(ValidationResult(
                    check_id="SEC-001",
                    check_name="Hardcoded Secret Detection",
                    validation_type=ValidationType.SECURITY,
                    level=ValidationLevel.CRITICAL,
                    passed=False,
                    message=f"{description} found",
                    details={
                        "pattern": pattern,
                        "matched_text": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                        "recommendation": "Use environment variables or secret management"
                    },
                    file_path=file_path,
                    line_number=content[:match.start()].count('\n') + 1,
                    suggestion="Store secrets in environment variables or use a secret manager"
                ))
    
    def _check_sql_injection(self, content: str, file_path: str):
        """Check for potential SQL injection vulnerabilities"""
        # Simple pattern matching for concatenated SQL queries
        patterns = [
            (r'execute\s*\(.*\+.*\)', "String concatenation in SQL execution"),
            (r'query\s*\(.*\+.*\)', "String concatenation in query"),
            (r'f["\'].*{.*}.*select', "f-string with SELECT statement"),
        ]
        
        for pattern, description in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                self.add_result(ValidationResult(
                    check_id="SEC-002",
                    check_name="SQL Injection Risk",
                    validation_type=ValidationType.SECURITY,
                    level=ValidationLevel.HIGH,
                    passed=False,
                    message=description,
                    details={
                        "pattern": pattern,
                        "risk": "Potential SQL injection vulnerability"
                    },
                    file_path=file_path,
                    suggestion="Use parameterized queries or ORM methods"
                ))
    
    def _check_xss_vulnerabilities(self, content: str, file_path: str):
        """Check for potential XSS vulnerabilities"""
        if file_path and file_path.endswith(('.js', '.jsx', '.ts', '.tsx', '.html')):
            # Look for innerHTML usage without sanitization
            if 'innerHTML' in content and not ('DOMPurify' in content or 'sanitize' in content):
                self.add_result(ValidationResult(
                    check_id="SEC-003",
                    check_name="XSS Risk",
                    validation_type=ValidationType.SECURITY,
                    level=ValidationLevel.HIGH,
                    passed=False,
                    message="innerHTML usage without sanitization",
                    details={
                        "risk": "Potential Cross-Site Scripting (XSS) vulnerability"
                    },
                    file_path=file_path,
                    suggestion="Use textContent or sanitize with DOMPurify"
                ))
    
    def _check_insecure_dependencies(self, content: str, file_path: str):
        """Check for known insecure dependencies"""
        if file_path and file_path.endswith(('package.json', 'requirements.txt', 'pyproject.toml')):
            insecure_packages = [
                'axios@<0.21.1', 'lodash@<4.17.21', 'moment@<2.29.1',
                'express@<4.17.1', 'request@<2.88.0'
            ]
            
            for package in insecure_packages:
                if package.split('@')[0] in content.lower():
                    self.add_result(ValidationResult(
                        check_id="SEC-004",
                        check_name="Insecure Dependency",
                        validation_type=ValidationType.SECURITY,
                        level=ValidationLevel.HIGH,
                        passed=False,
                        message=f"Potentially insecure dependency: {package}",
                        details={
                            "package": package,
                            "risk": "Known security vulnerabilities"
                        },
                        file_path=file_path,
                        suggestion=f"Update to latest secure version of {package.split('@')[0]}"
                    ))

class CodeQualityValidator(BaseValidator):
    """Validates code quality and best practices"""
    
    def validate(self, content: str, file_path: Optional[str] = None) -> List[ValidationResult]:
        self.results = []
        
        if file_path and file_path.endswith('.py'):
            self._validate_python_code(content, file_path)
        elif file_path and file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            self._validate_javascript_code(content, file_path)
        
        # General code quality checks
        self._check_file_length(content, file_path)
        self._check_complexity(content, file_path)
        
        return self.results
    
    def _validate_python_code(self, content: str, file_path: str):
        """Validate Python code quality"""
        try:
            # Parse Python code
            tree = ast.parse(content)
            
            # Check for broad exceptions
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:  # bare except
                        self.add_result(ValidationResult(
                            check_id="QUAL-001",
                            check_name="Bare Exception",
                            validation_type=ValidationType.CODE_QUALITY,
                            level=ValidationLevel.MEDIUM,
                            passed=False,
                            message="Bare except clause found",
                            details={
                                "issue": "Catching all exceptions can hide errors"
                            },
                            file_path=file_path,
                            line_number=node.lineno,
                            suggestion="Catch specific exceptions instead"
                        ))
            
            # Check line length (rough check)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if len(line) > 100:  # PEP 8 recommends 79, but we're lenient
                    self.add_result(ValidationResult(
                        check_id="QUAL-002",
                        check_name="Line Too Long",
                        validation_type=ValidationType.CODE_QUALITY,
                        level=ValidationLevel.LOW,
                        passed=False,
                        message=f"Line {i+1} exceeds 100 characters",
                        details={
                            "line_length": len(line),
                            "line_preview": line[:50] + "..." if len(line) > 50 else line
                        },
                        file_path=file_path,
                        line_number=i + 1,
                        suggestion="Break long lines for better readability"
                    ))
                    
        except SyntaxError as e:
            self.add_result(ValidationResult(
                check_id="QUAL-003",
                check_name="Syntax Error",
                validation_type=ValidationType.SYNTAX,
                level=ValidationLevel.CRITICAL,
                passed=False,
                message=f"Syntax error in Python code: {str(e)}",
                details={
                    "error": str(e),
                    "line": e.lineno if hasattr(e, 'lineno') else "unknown"
                },
                file_path=file_path,
                line_number=e.lineno if hasattr(e, 'lineno') else None
            ))
    
    def _validate_javascript_code(self, content: str, file_path: str):
        """Validate JavaScript/TypeScript code quality"""
        # Check for console.log statements (should be removed in production)
        console_log_matches = list(re.finditer(r'console\.(log|error|warn|info)\(', content))
        for match in console_log_matches:
            line_num = content[:match.start()].count('\n') + 1
            self.add_result(ValidationResult(
                check_id="QUAL-004",
                check_name="Console Statement",
                validation_type=ValidationType.CODE_QUALITY,
                level=ValidationLevel.LOW,
                passed=False,
                message="console statement found in code",
                details={
                    "statement": match.group(0),
                    "environment": "Should be removed in production"
                },
                file_path=file_path,
                line_number=line_num,
                suggestion="Use proper logging library or remove for production"
            ))
    
    def _check_file_length(self, content: str, file_path: str):
        """Check if file is too long"""
        lines = content.split('\n')
        if len(lines) > 500:
            self.add_result(ValidationResult(
                check_id="QUAL-005",
                check_name="File Too Long",
                validation_type=ValidationType.CODE_QUALITY,
                level=ValidationLevel.MEDIUM,
                passed=False,
                message=f"File has {len(lines)} lines (exceeds 500)",
                details={
                    "line_count": len(lines),
                    "recommendation": "Consider splitting into smaller modules"
                },
                file_path=file_path,
                suggestion="Split large files into smaller, focused modules"
            ))
    
    def _check_complexity(self, content: str, file_path: str):
        """Simple complexity check based on function/class count"""
        # Count functions and classes (rough estimate)
        function_count = len(re.findall(r'\b(def|function)\s+', content))
        class_count = len(re.findall(r'\bclass\s+', content))
        
        if function_count > 20 or class_count > 10:
            self.add_result(ValidationResult(
                check_id="QUAL-006",
                check_name="High Complexity",
                validation_type=ValidationType.CODE_QUALITY,
                level=ValidationLevel.MEDIUM,
                passed=False,
                message=f"High complexity: {function_count} functions, {class_count} classes",
                details={
                    "function_count": function_count,
                    "class_count": class_count,
                    "thresholds": {"functions": 20, "classes": 10}
                },
                file_path=file_path,
                suggestion="Refactor into smaller, more focused components"
            ))

class ValidationEngine:
    """
    Main validation engine that coordinates all validators
    """
    
    def __init__(self):
        self.validators = {
            "security": SecurityValidator(),
            "code_quality": CodeQualityValidator()
        }
        self.results = []
    
    def validate_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Validate a single file"""
        file_results = []
        
        for validator_name, validator in self.validators.items():
            validator_results = validator.validate(content, file_path)
            file_results.extend([r.to_dict() for r in validator_results])
        
        self.results.extend(file_results)
        return file_results
    
    def validate_project(self, project_files: Dict[str, str]) -> Dict[str, Any]:
        """Validate an entire project"""
        all_results = []
        
        for file_path, content in project_files.items():
            file_results = self.validate_file(file_path, content)
            all_results.extend(file_results)
        
        # Generate summary statistics
        summary = self._generate_summary(all_results)
        
        return {
            "success": summary["passed"],
            "summary": summary,
            "detailed_results": all_results,
            "total_files": len(project_files),
            "total_checks": len(all_results)
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from validation results"""
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed
        
        # Count by level
        by_level = {}
        by_type = {}
        
        for result in results:
            level = result["level"]
            v_type = result["validation_type"]
            
            by_level[level] = by_level.get(level, 0) + 1
            by_type[v_type] = by_type.get(v_type, 0) + 1
        
        return {
            "passed": failed == 0,
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 100,
            "by_level": by_level,
            "by_type": by_type,
            "has_critical": any(r["level"] == "critical" and not r["passed"] for r in results),
            "has_high": any(r["level"] == "high" and not r["passed"] for r in results)
        }
    
    def generate_report(self, output_format: str = "json") -> str:
        """Generate validation report in specified format"""
        summary = self._generate_summary(self.results)
        
        if output_format == "json":
            return json.dumps({
                "summary": summary,
                "results": self.results
            }, indent=2)
        elif output_format == "markdown":
            return self._generate_markdown_report(summary)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def _generate_markdown_report(self, summary: Dict[str, Any]) -> str:
        """Generate markdown report"""
        report = []
        report.append("# Validation Report")
        report.append("")
        
        # Summary section
        report.append("## Summary")
        report.append("")
        report.append(f"- **Status**: {'✅ PASSED' if summary['passed'] else '❌ FAILED'}")
        report.append(f"- **Total Checks**: {summary['total_checks']}")
        report.append(f"- **Passed**: {summary['passed_checks']}")
        report.append(f"- **Failed**: {summary['failed_checks']}")
        report.append(f"- **Pass Rate**: {summary['pass_rate']:.1f}%")
        report.append("")
        
        # Critical issues
        if summary["has_critical"]:
            report.append("## ⚠️ Critical Issues")
            report.append("")
            for result in self.results:
                if result["level"] == "critical" and not result["passed"]:
                    report.append(f"- **{result['check_name']}** in `{result.get('file_path', 'unknown')}`")
                    report.append(f"  - {result['message']}")
                    if result.get('suggestion'):
                        report.append(f"  - 💡 {result['suggestion']}")
                    report.append("")
        
        return "\n".join(report)

# Convenience functions
def validate_code_snippet(code: str, language: str = "python") -> Dict[str, Any]:
    """Validate a single code snippet"""
    engine = ValidationEngine()
    
    # Create a temporary file path based on language
    ext = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "jsx": ".jsx",
        "tsx": ".tsx"
    }.get(language, ".txt")
    
    file_path = f"snippet{ext}"
    results = engine.validate_file(file_path, code)
    summary = engine._generate_summary(results)
    
    return {
        "snippet_length": len(code),
        "language": language,
        "summary": summary,
        "results": results
    }

if __name__ == "__main__":
    # Example usage
    example_python_code = '''
def insecure_function():
    api_key = "sk-1234567890abcdef"
    query = "SELECT * FROM users WHERE id = " + user_input
    return execute(query)
    
def another_function():
    pass
    '''
    
    result = validate_code_snippet(example_python_code, "python")
    print(json.dumps(result, indent=2))
