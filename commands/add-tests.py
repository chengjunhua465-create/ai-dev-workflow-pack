#!/usr/bin/env python3
"""add-tests - Scan project for source files missing test files"""
import os

def main():
    patterns = {".py": ("tests/", "test_{name}.py"), ".ts": ("__tests__/", "{name}.test.ts"), ".js": ("__tests__/", "{name}.test.js"), ".rs": ("tests/", "{name}_test.rs")}
    found = False
    for root, dirs, files in os.walk("."):
        if any(x in root for x in ["node_modules",".git",".venv","target"]):
            continue
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in patterns:
                src = os.path.join(root, f)
                test_dir, test_pat = patterns[ext]
                name = os.path.splitext(f)[0]
                test_file = os.path.join(test_dir, test_pat.format(name=name))
                if not os.path.exists(test_file):
                    print(f"  Missing test: {test_file}  <-  {src}")
                    found = True
    if not found:
        print("All source files have corresponding test files!")

if __name__ == "__main__":
    main()
