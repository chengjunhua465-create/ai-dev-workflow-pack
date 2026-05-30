#!/usr/bin/env python3
"""
AI Developer Workflow Pack - Premium Command: Security Audit
Scans codebase for OWASP Top 10 vulnerabilities using pattern matching and AI analysis.

Usage: python3 security-audit.py [directory] [--json] [--ci]
"""
import os, json, sys, re, ast
from pathlib import Path
from collections import defaultdict

class SecurityAudit:
    SEVERITIES = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    
    RULES = {
        "sql_injection": {
            "pattern": r"(execute|exec|raw|query)\s*\(\s*f[\"']",
            "severity": "critical",
            "message": "SQL injection: f-string in query - use parameterized queries",
            "languages": ["python", "javascript"]
        },
        "hardcoded_secrets": {
            "pattern": r"(API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE_KEY)\s*=\s*[\"'][^\"']+[\"']",
            "severity": "critical",
            "message": "Hardcoded secret detected - use environment variables",
            "languages": ["all"]
        },
        "eval_usage": {
            "pattern": r"\beval\s*\(",
            "severity": "high",
            "message": "eval() usage - potential code injection",
            "languages": ["python", "javascript"]
        },
        "insecure_deserialization": {
            "pattern": r"pickle\.loads|yaml\.load\s*\(|node-serialize",
            "severity": "high",
            "message": "Insecure deserialization detected",
            "languages": ["python", "javascript"]
        },
        "path_traversal": {
            "pattern": r"open\s*\(\s*f[\"'][^)]*\.\.\.",
            "severity": "high",
            "message": "Potential path traversal with user input",
            "languages": ["python"]
        },
        "command_injection": {
            "pattern": r"os\.system|subprocess\.Popen|child_process\.exec\b",
            "severity": "high",
            "message": "Shell command execution - validate inputs",
            "languages": ["all"]
        },
        "debug_enabled": {
            "pattern": r"DEBUG\s*=\s*True|debug=True|app\.run\(.*debug=True",
            "severity": "medium",
            "message": "Debug mode enabled in production",
            "languages": ["python"]
        },
        "no_auth": {
            "pattern": r"@app\.route|@router\.(get|post|put|delete)",
            "severity": "medium",
            "message": "Route without auth decorator - verify access control",
            "languages": ["python"]
        },
        "insecure_cors": {
            "pattern": r"CORS\(.*origins?\s*=\s*[\"']\*[\"']",
            "severity": "medium",
            "message": "CORS allows all origins (*)",
            "languages": ["python", "javascript"]
        },
        "weak_hash": {
            "pattern": r"md5\s*\(|sha1\s*\(",
            "severity": "medium",
            "message": "Weak hash algorithm - use SHA-256 or bcrypt",
            "languages": ["all"]
        },
    }

    def __init__(self, directory=".", json_output=False, ci_mode=False):
        self.directory = Path(directory)
        self.json_output = json_output
        self.ci_mode = ci_mode
        self.findings = []
        self.file_count = 0

    def scan(self):
        extensions = {".py": "python", ".js": "javascript", ".ts": "typescript", 
                     ".jsx": "javascript", ".tsx": "typescript", ".go": "go",
                     ".rs": "rust", ".rb": "ruby", ".php": "php"}
        
        for ext, lang in extensions.items():
            for f in self.directory.rglob(f"*{ext}"):
                if any(p in str(f) for p in ["node_modules", ".venv", "venv", 
                                              "__pycache__", ".git", "dist", "build"]):
                    continue
                self.file_count += 1
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    self._check_file(f, content, lang)
                except Exception:
                    continue
        
        return self._report()

    def _check_file(self, filepath, content, lang):
        for rule_name, rule in self.RULES.items():
            if rule["languages"][0] != "all" and lang not in rule["languages"]:
                continue
            matches = re.finditer(rule["pattern"], content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                context_start = max(0, match.start() - 40)
                context_end = min(len(content), match.end() + 40)
                context = content[context_start:context_end].replace("\n", " ")
                
                self.findings.append({
                    "rule": rule_name,
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "file": str(filepath.relative_to(self.directory)),
                    "line": line_num,
                    "match": match.group(),
                    "context": context.strip()
                })

    def _report(self):
        by_severity = defaultdict(list)
        for f in self.findings:
            by_severity[f["severity"]].append(f)
        
        if self.json_output:
            return json.dumps({
                "scanned_files": self.file_count,
                "total_findings": len(self.findings),
                "by_severity": {k: len(v) for k, v in by_severity.items()},
                "findings": self.findings
            }, indent=2)
        
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"  SECURITY AUDIT REPORT")
        lines.append(f"  Files scanned: {self.file_count}")
        lines.append(f"  Total findings: {len(self.findings)}")
        lines.append(f"{'='*60}\n")
        
        for severity in ["critical", "high", "medium", "low"]:
            items = by_severity.get(severity, [])
            if not items:
                continue
            icon = self.SEVERITIES[severity]
            lines.append(f"  {icon} {severity.upper()} ({len(items)})")
            lines.append(f"  {'─'*50}")
            for f in items:
                lines.append(f"    {f['file']}:{f['line']}")
                lines.append(f"    {f['message']}")
                lines.append(f"    Match: {f['match'][:60]}")
                lines.append("")
        
        if not self.findings:
            lines.append("  ✅ No issues found! Codebase looks secure.\n")
        
        total = len(self.findings)
        if self.ci_mode:
            if total > 0:
                lines.append(f"\n  ❌ CI FAILED: {total} security issue(s) found")
            else:
                lines.append(f"\n  ✅ CI PASSED")
        
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)

if __name__ == "__main__":
    args = sys.argv[1:]
    directory = "."
    json_output = "--json" in args
    ci_mode = "--ci" in args
    for a in args:
        if not a.startswith("--") and Path(a).exists():
            directory = a
    
    auditor = SecurityAudit(directory, json_output, ci_mode)
    result = auditor.scan()
    print(result)
    sys.exit(1 if auditor.findings else 0)
