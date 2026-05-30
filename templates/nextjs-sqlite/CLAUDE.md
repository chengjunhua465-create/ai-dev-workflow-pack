# Next.js 15 + SQLite SaaS Template

## Project Overview
A modern Next.js 15 SaaS application with SQLite database, authentication, Stripe payments, and full TypeScript support.

## Tech Stack
- Framework: Next.js 15 (App Router)
- Database: SQLite via Prisma ORM
- Auth: NextAuth.js v5 with email/password
- Payments: Stripe
- UI: Tailwind CSS + shadcn/ui
- Language: TypeScript (strict mode)
- Testing: Vitest + Playwright

## Key Conventions

### Architecture
- /app - App Router pages and API routes
- /components - Reusable React components (shadcn/ui)
- /lib - Utility functions and configurations
- /prisma - Database schema and migrations
- /types - TypeScript type definitions
- /tests - Test files mirroring source structure
