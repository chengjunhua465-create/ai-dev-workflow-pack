# React 19 + Vite SPA

## Overview
Modern single-page app with React 19, Vite 6, TanStack Router, Tailwind CSS v4.

## Tech Stack
Framework: React 19
Build: Vite 6
Routing: TanStack Router (type-safe)
State: TanStack Query (server state)
Styling: Tailwind CSS v4
Components: shadcn/ui
Testing: Vitest + React Testing Library
Storybook: v8
Language: TypeScript (strict mode)
Format: Biome

## Architecture
- src/routes/       Route definitions + lazy loading
- src/components/   UI components (shadcn/ui base)
- src/features/     Feature modules (auth, dashboard, etc.)
- src/hooks/        Custom React hooks
- src/lib/          Utilities, API client
- src/types/        TypeScript type definitions
- tests/            Component + integration tests
- stories/          Storybook stories

## Code Rules
- React 19 patterns (use, useOptimistic, useFormStatus)
- TanStack Router for type-safe routing
- TanStack Query for server state management
- shadcn/ui components in components/ui/
- Feature-based directory structure
- Loading states with React Suspense

## Commands
- npm run dev           Vite dev server (HMR)
- npm run build         Production build
- npm run test          Vitest test runner
- npm run storybook     Storybook dev server
- npx shadcn add [comp] Add shadcn/ui component
- npm run format        Biome format
- npm run lint          Biome lint