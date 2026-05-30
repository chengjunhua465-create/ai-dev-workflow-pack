# Rust + Axum Web Service

## Overview
High-performance async web service with Axum, SQLx, Tokio, Serde.

## Tech Stack
Web: Axum 0.8
DB: SQLx (PostgreSQL)
Async: Tokio (multi-threaded)
Serialization: Serde + serde_json
Auth: JWT (jsonwebtoken crate)
Logging: tracing + tracing-subscriber
Language: Rust (edition 2024)

## Architecture
- src/main.rs       App entry, router setup
- src/routes/       Route handler modules
- src/models/       Database types + SQL queries
- src/middleware/    Auth, logging, CORS layers
- src/errors/       Custom error types (thiserror)
- src/config/       Environment configuration
- migrations/       SQLx migration files
- tests/            Integration tests

## Code Rules
- Use thiserror for error types
- Axum State for shared app state
- Tower middleware layers for auth/logging
- SQLx query-as for compile-time SQL checking
- tracing spans for request logging

## Commands
- cargo run               Dev server
- cargo test              Run all tests
- cargo clippy            Lint with clippy
- cargo build --release   Production binary
- sqlx migrate run        Apply migrations
- sqlx prepare            Update offline query cache