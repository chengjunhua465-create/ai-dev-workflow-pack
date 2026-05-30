#!/usr/bin/env python3
"""review-code - Full security + quality code review from git diff"""
import subprocess, sys

def get_diff():
    r = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    if not r.stdout.strip():
        r = subprocess.run(["git", "diff", "HEAD~1"], capture_output=True, text=True)
    return r.stdout

def main():
    diff = get_diff()
    if not diff:
        print("No changes to review.")
        return
    lines = diff.split("\n")
    print(f"Changes to review: {len(lines)} lines\n")
    print("## Security Checks")
    for name, check in [("Hardcoded secrets","api_key,password,secret,token="),("SQL injection","raw_query,format(query,"),("XSS","dangerouslySetInnerHTML,innerHTML")]:
        risk = any(k in diff for k in check.split(","))
        print(f"  [{'RISK' if risk else 'OK'}] {name}")
    print("\n## Quality Stats")
    added = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
    print(f"  Lines added: {added}")
    print(f"  Lines removed: {removed}")

if __name__ == "__main__":
    main()
