#!/usr/bin/env python3
"""db-migrate - Database migration helper"""
import os, sys

def detect():
    if os.path.exists("prisma/schema.prisma"): return "prisma"
    if os.path.exists("alembic.ini"): return "alembic"
    if os.path.exists("migrations"): return "sqlx"
    return None

def main():
    fw = detect()
    if not fw:
        print("No supported DB framework (Prisma, Alembic, SQLx).")
        return
    name = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "auto_migration"
    print(f"Framework: {fw}\nName: {name}\n")
    steps = {"prisma":["1. Validate: npx prisma validate",f"2. Create: npx prisma migrate dev --name {name}","3. Deploy: npx prisma migrate deploy","4. Generate: npx prisma generate"],"alembic":[f"1. Create: alembic revision --autogenerate -m {name}","2. Review migration","3. Apply: alembic upgrade head"],"sqlx":[f"1. Create: sqlx migrate add -r {name}","2. Write up/down SQL","3. Apply: sqlx migrate run"]}
    for s in steps[fw]:
        print(f"  {s}")

if __name__ == "__main__":
    main()
