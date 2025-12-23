"""
Security Scanner Module
Advanced security vulnerability detection
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .validator import ValidationResult, ValidationLevel, ValidationType

@dataclass
class SecurityFinding:
    """Security finding with remediation guidance"""
    vulnerability_id: str
    title: str
    description: str
    severity: str  # critical, high, medium, low
    cwe_id: Optional[str] = None
    remediation: Optional[str] = None
    references: List[str] = None
    
    def to_validation_result(self, file_path: str, line_number: int = None) -> ValidationResult:
        """Convert to ValidationResult format"""
        return ValidationResult(
            check_id=f"SEC-{self.vulnerability_id}",
            check_name=self.title,
            validation_type=ValidationType.SECURITY,
            level=ValidationLevel(self.severity),
            passed=False,
            message=self.description,
            details={
                "cwe_id": self.cwe_id,
                "references": self.references
            },
            file_path=file_path,
            line_number=line_number,
            suggestion=self.remediation
        )

class SecurityScanner:
    """Advanced security vulnerability scanner"""
    
    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.findings: List[SecurityFinding] = []
    
    def _load_vulnerability_patterns(self) -> List[Dict[str, Any]]:
        """Load vulnerability detection patterns"""
        return [
            {
                "id": "CWE-78",
                "title": "OS Command Injection",
                "pattern": r'(os\.system|subprocess\.call|subprocess\.Popen|exec|eval)\s*\(.*\+.*\)',
                "severity": "critical",
                "description": "Potential OS command injection vulnerability",
                "remediation": "Use safe APIs that separate commands from arguments"
            },
            {
                "id": "CWE-79",
                "title": "Cross-Site Scripting (XSS)",
                "pattern": r'innerHTML\s*=.*(<script>|javascript:)',
                "severity": "high",
                "description": "Potential XSS vulnerability through innerHTML assignment",
                "remediation": "Use textContent or sanitize user input"
            },
            {
                "id": "CWE-89",
                "title": "SQL Injection",
                "pattern": r'(execute|query|exec)\s*\(.*["\'].*\+(user|input).*\)',
                "severity": "critical",
                "description": "Potential SQL injection vulnerability",
                "remediation": "Use parameterized queries or ORM"
            },
            {
                "id": "CWE-89-ASSIGN",
                "title": "SQL Injection (string concatenation)",
                "pattern": r'["\'].*\b(select|insert|update|delete)\b.*["\']\s*\+\s*\w+',
                "severity": "critical",
                "description": "Potential SQL injection via string concatenation with user input",
                "remediation": "Use parameterized queries or ORM"
            },
            {
                "id": "CWE-259",
                "title": "Use of Hard-coded Password",
                "pattern": r'password\s*=\s*["\'][^"\']+["\']',
                "severity": "critical",
                "description": "Hard-coded password found",
                "remediation": "Use environment variables or secure credential storage"
            },
            {
                "id": "CWE-798",
                "title": "Use of Hard-coded Credentials",
                "pattern": r'(api[_-]?key|secret|token)\s*=\s*["\'][^"\']+["\']',
                "severity": "critical",
                "description": "Hard-coded credentials found",
                "remediation": "Use environment variables or secret management"
            }
        ]
    
    def scan_file(self, file_path: str, content: str) -> List[ValidationResult]:
        """Scan a file for security vulnerabilities"""
        results = []
        
        for vuln in self.vulnerability_patterns:
            matches = re.finditer(vuln["pattern"], content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                finding = SecurityFinding(
                    vulnerability_id=vuln["id"],
                    title=vuln["title"],
                    description=vuln["description"],
                    severity=vuln["severity"],
                    cwe_id=vuln["id"],
                    remediation=vuln["remediation"],
                    references=[f"https://cwe.mitre.org/data/definitions/{vuln['id'].split('-')[1]}.html"]
                )
                
                line_number = content[:match.start()].count('\n') + 1
                results.append(finding.to_validation_result(file_path, line_number))
                self.findings.append(finding)
        
        return results
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        severity_counts = {}
        for finding in self.findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        
        return {
            "total_findings": len(self.findings),
            "severity_counts": severity_counts,
            "findings": [
                {
                    "id": f.vulnerability_id,
                    "title": f.title,
                    "severity": f.severity,
                    "description": f.description,
                    "remediation": f.remediation
                }
                for f in self.findings
            ],
            "risk_level": self._calculate_risk_level(severity_counts)
        }
    
    def _calculate_risk_level(self, severity_counts: Dict[str, int]) -> str:
        """Calculate overall risk level"""
        if severity_counts.get("critical", 0) > 0:
            return "CRITICAL"
        elif severity_counts.get("high", 0) > 3:
            return "HIGH"
        elif severity_counts.get("high", 0) > 0 or severity_counts.get("medium", 0) > 5:
            return "MEDIUM"
        elif severity_counts.get("low", 0) > 0:
            return "LOW"
        else:
            return "NONE"

class LLMFingerprintDetector:
    """
    Detects LLM-generated code patterns
    Helps identify code that might need human review
    """
    
    def __init__(self):
        self.llm_patterns = [
            # Common LLM code patterns
            (r'# This (function|class) (handles|manages|implements)', "LLM-style comment"),
            (r'"""\s*[A-Z][^\.]*\.\s*\n\s*[A-Z][^\.]*\.', "LLM-style docstring"),
            (r'try:\s*\n\s*.*\s*\nexcept Exception as e:\s*\n\s*.*print\(f', "LLM-style error handling"),
            (r'# Note:|# Important:|# Please note:', "LLM instructional comment"),
            (r'def\s+\w+\(.*\):\s*\n\s*"""\s*\n\s*Args:', "LLM-style Google docstring"),
        ]
    
    def detect_fingerprints(self, content: str) -> List[Dict[str, Any]]:
        """Detect LLM fingerprint patterns in code"""
        findings = []
        
        for pattern, description in self.llm_patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                findings.append({
                    "pattern": description,
                    "confidence": "medium",
                    "line_number": line_number,
                    "matched_text": match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0),
                    "suggestion": "Review this code section for correctness and security"
                })
        
        return findings
    
    def calculate_llm_score(self, content: str) -> float:
        """Calculate LLM fingerprint score (0-1)"""
        total_patterns = len(self.llm_patterns)
        if total_patterns == 0:
            return 0.0
        
        matches = 0
        for pattern, _ in self.llm_patterns:
            if re.search(pattern, content, re.MULTILINE):
                matches += 1
        
        return min(matches / total_patterns, 1.0)

# Export convenience functions
def scan_for_security_vulnerabilities(file_path: str, content: str) -> Dict[str, Any]:
    """Convenience function for security scanning"""
    scanner = SecurityScanner()
    results = scanner.scan_file(file_path, content)
    report = scanner.generate_security_report()
    
    return {
        "file": file_path,
        "vulnerabilities_found": len(results),
        "security_report": report,
        "validation_results": [r.to_dict() for r in results]
    }

def detect_llm_generated_code(content: str) -> Dict[str, Any]:
    """Detect if code appears to be LLM-generated"""
    detector = LLMFingerprintDetector()
    fingerprints = detector.detect_fingerprints(content)
    llm_score = detector.calculate_llm_score(content)
    
    return {
        "llm_score": llm_score,
        "likely_llm_generated": llm_score > 0.5,
        "fingerprints_found": len(fingerprints),
        "fingerprints": fingerprints,
        "interpretation": {
            "0-0.3": "Likely human-written or heavily edited",
            "0.3-0.6": "Mixed human/LLM authorship",
            "0.6-1.0": "Likely LLM-generated, review recommended"
        }
    }

if __name__ == "__main__":
    # Example usage
    example_code = '''
def process_user_input(user_input):
    """Process user input safely.
    
    Args:
        user_input (str): The user input to process
        
    Returns:
        str: Processed result
    """
    try:
        # Important: Sanitize input to prevent XSS
        sanitized = user_input.replace("<", "&lt;").replace(">", "&gt;")
        return f"Processed: {sanitized}"
    except Exception as e:
        print(f"Error processing input: {e}")
        return ""
    '''
    
    # Security scan
    security_result = scan_for_security_vulnerabilities("example.py", example_code)
    print("Security Scan Results:")
    print(json.dumps(security_result, indent=2))
    
    # LLM detection
    llm_result = detect_llm_generated_code(example_code)
    print("\nLLM Detection Results:")
    print(json.dumps(llm_result, indent=2))
