# Express.js + Prisma REST API

## Overview
TypeScript REST API with Express.js, Prisma ORM, PostgreSQL, Zod validation.

## Tech Stack
Runtime: Node.js 22+
Framework: Express.js
Database: PostgreSQL via Prisma
Validation: Zod
Auth: JWT + bcrypt
Testing: Vitest + supertest
Docs: Swagger/OpenAPI (swagger-jsdoc)
Container: Docker + docker-compose
Language: TypeScript (strict mode)

## Architecture
- src/routes/       Express route definitions
- src/controllers/  Request handlers (thin)
- src/services/     Business logic layer
- src/middleware/    Auth, validation, error handling
- src/validators/   Zod schemas
- prisma/           Schema + migrations
- tests/            Vitest test files

## Code Rules
- Controller -> Service pattern (controllers are thin)
- Zod middleware for input validation
- Consistent error: {success: false, error: {code, message}}
- Prisma transactions for multi-table operations

## Commands
- npm run dev           Dev with hot reload
- npm run build         TypeScript compile
- npm start             Production mode
- npm test              Vitest test runner
- npx prisma studio     Database GUI
- npx prisma migrate    Create migration
- docker-compose up     Full stack with DB