#!/usr/bin/env python3
"""generate-changelog - Generate CHANGELOG.md from git history"""
import subprocess
from collections import defaultdict
from datetime import date

def categorize(msg):
    prefixes = {"Added":["add","feature","feat","new","create","implement"],"Fixed":["fix","bug","patch","hotfix","resolve"],"Changed":["change","update","refactor","improve","migrate"],"Removed":["remove","delete","deprecate","drop"],"Documentation":["docs","document","readme"]}
    for cat, keywords in prefixes.items():
        if any(k in msg.lower() for k in keywords):
            return cat
    return "Other"

def main():
    r = subprocess.run(["git","describe","--tags","--abbrev=0"], capture_output=True, text=True)
    last_tag = r.stdout.strip() if r.returncode == 0 else None
    if last_tag:
        r = subprocess.run(["git","log",f"{last_tag}..HEAD","--oneline"], capture_output=True, text=True)
    else:
        r = subprocess.run(["git","log","--oneline"], capture_output=True, text=True)
    commits = [l for l in r.stdout.strip().split("\n") if l]
    if not commits:
        print("No commits found.")
        return
    grouped = defaultdict(list)
    for c in commits:
        parts = c.split(" ", 1)
        h, msg = parts[0], parts[1] if len(parts) > 1 else ""
        grouped[categorize(msg)].append(f"- {msg} ({h[:7]})")
    tag = last_tag or "v1.0.0"
    lines = [f"# Changelog\n", f"## [{tag}] - {date.today()}\n"]
    for cat in ["Added","Changed","Fixed","Removed","Documentation","Other"]:
        if grouped[cat]:
            lines.append(f"### {cat}")
            lines.extend(grouped[cat])
            lines.append("")
    print("\n".join(lines))
    print("\n---")
    print("To save: python3 generate-changelog.py > CHANGELOG.md")

if __name__ == "__main__":
    main()
