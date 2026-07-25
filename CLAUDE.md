# APISense Backend - Claude Instructions

## Project Overview

APISense is a production SaaS backend built with:

- FastAPI
- PostgreSQL (Neon)
- SQLAlchemy 2.x Async ORM
- Alembic
- Pydantic v2
- JWT Authentication
- Brevo Transactional Email

The goal is to build a scalable, maintainable, production-ready backend.

---

# Engineering Standards

Write code as if it will be maintained by senior backend engineers for years.

Prioritize:

- Readability
- Maintainability
- Reusability
- Simplicity

Avoid clever code.

Prefer explicit implementations.

---

# Architecture

Always follow this architecture:

Router
↓

Service

↓

Repository

↓

Database

Responsibilities:

- Routers should only validate requests, call services, and return responses.
- Services contain business logic.
- Repositories contain only persistence logic.
- Models define database structure.
- Schemas define request and response models.

Do not mix responsibilities.

---

# Code Quality

Write production-ready code.

Follow SOLID principles where appropriate.

Prefer composition over inheritance.

Avoid unnecessary abstractions.

Avoid premature optimization.

Keep methods focused on a single responsibility.

Write reusable code.

Avoid duplication.

---

# Existing Code

Before creating:

- helper
- utility
- repository
- service
- abstraction
- schema

always check whether something similar already exists.

Prefer extending existing code over creating duplicate implementations.

---

# Python Standards

Use Python 3.13.

Use full type hints.

Use async correctly.

Write modern SQLAlchemy 2.x code.

Avoid deprecated APIs.

Prefer dependency injection.

---

# Database

Use Alembic for schema changes.

Never manually modify production schema.

Design proper indexes.

Avoid N+1 queries.

Store timestamps in UTC.

Never store secrets or tokens in plain text.

Hash tokens before persisting them.

---

# API Standards

Build RESTful APIs.

Use consistent naming.

Use consistent response schemas.

Return proper HTTP status codes.

Raise domain-specific exceptions.

Never leak sensitive information in API responses.

---

# Security

Use Argon2 for passwords.

Validate all inputs.

Hash verification tokens.

Hash refresh tokens.

Never expose internal errors.

Fail securely.

---

# Error Handling

Do not catch generic exceptions unless absolutely necessary.

Create meaningful domain exceptions.

Log meaningful errors.

Do not silently ignore failures.

---

# Comments

Keep comments minimal.

Only comment:

- business rules
- security decisions
- complex implementation details

Do not comment obvious code.

Prefer self-documenting code.

---

# Naming

Use descriptive names.

Avoid abbreviations.

Avoid single-letter variables except loop counters.

Keep naming consistent across the project.

---

# Testing

Before considering a task complete:

- verify imports
- run migrations
- verify Alembic has no drift
- test against the real Neon database whenever applicable
- verify endpoints work end-to-end

Explain every file created or modified.

---

# Refactoring

If a requested implementation can be significantly improved:

- explain the trade-offs
- ask before changing the architecture

Do not silently introduce architectural changes.

---

# Code Style

Keep functions small.

Prefer early returns.

Avoid deep nesting.

Avoid duplicate logic.

Avoid magic strings.

Extract reusable constants when appropriate.

---

# Goal

Every implementation should look like it was written by an experienced Senior Backend Engineer building a production SaaS.

# Communication

Before implementing:

- Check the existing codebase.
- Reuse existing components whenever possible.
- If a better architectural approach exists, explain the trade-offs before implementing.

After implementing:

- Explain the architectural decisions.
- Explain every file created or modified.
- Describe how the feature was verified.

## Code Quality

Every feature should satisfy these requirements before it is considered complete:

- Clean architecture
- Single responsibility
- Dependency inversion
- Atomic database transactions
- No duplicated business logic
- Async-safe implementation
- Centralized exception handling
- Strong input validation
- Security-first design
- End-to-end verification
- Automated tests for business-critical flows
