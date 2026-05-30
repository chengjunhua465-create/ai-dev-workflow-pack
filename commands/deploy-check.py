#!/usr/bin/env python3
"""deploy-check - Pre-deployment checklist"""
import subprocess, os

def check(name, cmd, shell=False):
    try:
        if shell:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        else:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return r.returncode == 0
    except:
        return False

def main():
    print("=== Pre-Deployment Checklist ===\n")
    checks = []
    ok = check("Git clean", ["git", "diff", "--stat"])
    checks.append(("Git working tree clean", ok, "git status"))
    r = subprocess.run(["git","branch","--show-current"], capture_output=True, text=True, timeout=5)
    branch = r.stdout.strip()
    checks.append((f"On main/master (current: {branch})", branch in ("main","master"), "git checkout main"))
    if os.path.exists("package.json"):
        for label, cmd in [("Build","npm run build"),("Lint","npm run lint"),("Tests","npm test")]:
            ok = check(label, cmd, shell=True)
            checks.append((f"npm: {label}", ok, cmd))
    if os.path.exists("Cargo.toml"):
        for label, cmd in [("Build","cargo build"),("Tests","cargo test")]:
            ok = check(label, cmd.split())
            checks.append((f"cargo: {label}", ok, cmd))
    all_pass = True
    for name, passed, fix in checks:
        status = "PASS" if passed else "FAIL"
        if not passed: all_pass = False
        print(f"  [{status}] {name}")
        if not passed:
            print(f"         Fix: {fix}")
    print(f"\n{'READY TO DEPLOY!' if all_pass else 'Fix issues before deploying.'}")

if __name__ == "__main__":
    main()
