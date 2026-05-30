#!/usr/bin/env python3
"""
AI Developer Workflow Pack - Premium Command: Performance Profiler
Analyzes Python/JavaScript code for performance bottlenecks.

Usage: python3 performance-profile.py [directory] [--json] [--ci]
"""
import os, sys, re, json, ast
from pathlib import Path
from collections import defaultdict, Counter

class PerformanceProfiler:
    PATTERNS = {
        "nested_loops": {
            "pattern": r"(for\s+.*:\s*$\s*^\s+for\s+.*:)|(for\s+.*\{[^}]*for\s+.*\{)",
            "severity": "high",
            "message": "Nested loops detected - O(n²) complexity, consider optimization",
            "detail": "Use dict lookups, set operations, or Pandas vectorization"
        },
        "inefficient_list": {
            "pattern": r"\[\s*.*\s+for\s+.*\s+in\s+.*\s+for\s+",
            "severity": "medium",
            "message": "Nested list comprehension - consider generator or alternative structure",
        },
        "sync_api_call": {
            "pattern": r"requests\.(get|post|put|delete)\s*\(",
            "severity": "medium",
            "message": "Synchronous HTTP call - use httpx.AsyncClient or aiohttp for I/O bound work",
        },
        "large_allocation": {
            "pattern": r"\.read\(\s*\)\s*$|\.read\(\s*\)\s*\.split|\"\"\.join\(list|pd\.concat\(.*\[",
            "severity": "medium", 
            "message": "Potential large memory allocation - consider streaming/chunking",
        },
        "unoptimized_db": {
            "pattern": r"\.filter\(.*\.all\(\)|\.objects\.all\(\)\s*$|SELECT\s+\*\s+FROM",
            "severity": "medium",
            "message": "Unoptimized query - consider select_related/prefetch_related or specific columns",
        },
        "busy_wait": {
            "pattern": r"time\.sleep\s*\(\s*0\.\d+\s*\)|while\s+True:.*time\.sleep|setInterval\(.*\d{1,3}\)",
            "severity": "low",
            "message": "Busy wait / polling detected - consider event-driven approach",
        },
        "no_cache": {
            "pattern": r"@app\.route|@router\.get",
            "severity": "low",
            "message": "Route without caching - consider @lru_cache or redis for repeated calls",
            "context": "Check if caching strategy is needed"
        },
    }

    def __init__(self, directory=".", json_output=False):
        self.directory = Path(directory)
        self.json_output = json_output
        self.findings = []
        
    def scan(self):
        for f in self.directory.rglob("*.py"):
            if any(p in str(f) for p in ["node_modules", ".venv", "venv", "__pycache__", ".git"]):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                self._analyze(f, content)
            except Exception:
                continue
        
        return self._report()
    
    def _analyze(self, filepath, content):
        lines = content.split("\n")
        for rule_name, rule in self.PATTERNS.items():
            for i, line in enumerate(lines, 1):
                if re.search(rule["pattern"], line, re.MULTILINE):
                    self.findings.append({
                        "rule": rule_name,
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "file": str(filepath.relative_to(self.directory)),
                        "line": i,
                        "code": line.strip()[:100],
                    })
    
    def _report(self):
        if self.json_output:
            return json.dumps({"findings": self.findings, "total": len(self.findings)}, indent=2)
        
        lines = [f"\n{'='*60}", "  PERFORMANCE PROFILE REPORT",
                 f"  Files analyzed: {len(set(f['file'] for f in self.findings))}",
                 f"  Total findings: {len(self.findings)}", f"{'='*60}\n"]
        
        for sev in ["high", "medium", "low"]:
            items = [f for f in self.findings if f["severity"] == sev]
            if not items:
                continue
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[sev]
            lines.append(f"  {icon} {sev.upper()} ({len(items)})")
            lines.append(f"  {'─'*50}")
            for f in items[:10]:
                lines.append(f"    {f['file']}:{f['line']}  {f['message']}")
                lines.append(f"    {f['code']}\n")
            if len(items) > 10:
                lines.append(f"    ... and {len(items)-10} more\n")
        
        if not self.findings:
            lines.append("  ✅ No performance issues found!\n")
        
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)

if __name__ == "__main__":
    args = sys.argv[1:]
    directory = "."
    json_output = "--json" in args
    for a in args:
        if not a.startswith("--") and Path(a).exists():
            directory = a
    profiler = PerformanceProfiler(directory, json_output)
    print(profiler.scan())
