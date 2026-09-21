# Technology decisions

This document records the current technology choices for Raise 'n Rescue and the engineering reasoning behind them.

These choices support the MVP architecture and may change if the project develops requirements that justify a different approach. Changes to significant technology choices should be recorded in the decision log.

## 1. Technology stack overview

| Area | Technology | Role |
| --- | --- | --- |
| Frontend | React + TypeScript | User interface and client-side application behaviour |
| Frontend styling | CSS Modules | Component-level styling and UI isolation |
| Backend | FastAPI + Python | REST API and application/domain logic |
| Persistence | SQLAlchemy | Python database access and ORM mapping |
| Database | PostgreSQL | Relational persistence and structural data integrity |
| Database migrations | Alembic | Versioned database schema changes |
| API style | REST | Communication between frontend and backend |
| Authentication | Server-managed sessions | Browser authentication using secure HTTP-only cookies |

The project uses these technologies as parts of a single modular monolith rather than as independent services.

## 2. Frontend: React and TypeScript

React is used for the frontend because the product requires multiple interactive workflows rather than a collection of static pages.

The frontend needs to support animal discovery, filtering, animal profiles, matching results, favourites, adopter profiles, application forms, application tracking, and rescue staff workflows.

TypeScript is used alongside React to provide static typing for frontend state, API data, component props, and application logic.

The frontend is responsible for presentation and user interaction, while the backend remains authoritative for business rules, authorisation, matching, and application workflows.

CSS Modules are the intended styling approach so that component styles remain locally scoped and do not depend on a large global styling system.

## 3. Backend: FastAPI and Python

FastAPI is the backend framework for the project.

Python was selected for the backend because it allows the project to focus on the engineering problems that matter most for this portfolio project: API design, relational data modelling, authentication, authorisation, business rules, testing, and deployment.

Python also keeps the backend technology aligned with the user's existing experience and provides a useful foundation for future work involving data analysis or machine learning.

FastAPI provides a clear foundation for a REST API and works well with Pydantic for request and response validation.

The backend follows the layered architecture documented in `architecture.md`. API routes handle HTTP concerns, services contain business logic, repositories handle persistence, and PostgreSQL provides structural data integrity.

### 3.1 Why not Spring Boot for this project?

Spring Boot and Java were originally considered because of their relevance to enterprise software and the user's existing Java experience.

The decision was later reversed in favour of FastAPI and Python. The main reason was to avoid spending project time learning or configuring a larger backend ecosystem when the main learning goals are API design, architecture, database design, security, testing, and real application workflows.

Spring Boot remains a useful technology to learn for a future project, but it is not being added to Raise 'n Rescue simply for CV breadth.

## 4. Database: PostgreSQL

PostgreSQL is the primary database because Raise 'n Rescue has strongly relational data and workflows.

The domain includes users, rescue organisations, facilities, animals, adopter profiles, favourites, applications, application status history, and several structured many-to-many relationships.

PostgreSQL provides the relational constraints needed to protect data integrity, including foreign keys, unique constraints, indexes, check constraints, and native enum types.

The database is treated as a structural integrity boundary. Application-level decisions such as whether an application may be submitted or whether a status transition is valid remain in the backend service layer.

PostgreSQL also provides a strong foundation for future reporting and data analysis without introducing a separate analytical database during the MVP.

## 5. Persistence: SQLAlchemy

SQLAlchemy is used as the Python database access and ORM layer.

The project uses SQLAlchemy models to represent the domain entities and relationships defined in the data model.

SQLAlchemy was selected because it provides explicit control over relational mappings and database queries while still reducing repetitive persistence code.

The application will use a repository boundary around database access. This keeps SQLAlchemy-specific persistence concerns out of API routes and allows business logic to remain independently testable.

The current implementation includes the SQLAlchemy engine and domain models. Database session management and repositories are still to be implemented.

## 6. Database migrations: Alembic

Alembic is used to manage versioned changes to the PostgreSQL schema.

Database schema changes should be represented by migration files rather than being applied manually to the development database.

This makes schema changes reproducible and gives the project a history of how the database structure evolved.

The initial migration has already been created and applied. Future changes to the data model should be introduced through new Alembic revisions.

## 7. API style: REST

The frontend and backend communicate through a REST API under the `/api/*` path.

REST was selected because the MVP consists of conventional resources and workflows such as animals, adopter profiles, favourites, applications, organisations, and facilities.

The API design keeps HTTP concerns separate from business logic. Routes validate and translate requests, services apply business rules, and repositories handle persistence.

The frontend does not access PostgreSQL directly and does not contain authoritative business rules.

The current backend exposes only the health endpoint. The remaining REST API is designed but has not yet been implemented.

## 8. Authentication: server-managed sessions

The application is designed to use server-managed sessions with an HTTP-only browser cookie.

The browser stores only the session identifier in the cookie. The backend maintains the authenticated session and uses it to identify the user on subsequent requests.

This approach was selected instead of storing authentication tokens in browser local storage because authentication is part of a browser-based application and the backend needs a clear server-side security boundary.

The planned cookie configuration includes HttpOnly, Secure when HTTPS is used, an appropriate SameSite policy, and a limited session lifetime.

CSRF protection is also required because authenticated requests rely on a browser cookie.

Authentication, session persistence, CSRF protection, and authenticated API access are designed but not implemented yet.

## 9. Modular monolith

Raise 'n Rescue uses a modular monolith for the MVP.

The frontend, backend, and database are separate application components, but the backend itself is structured as one application rather than being split into independent services.

This keeps deployment, local development, debugging, and testing manageable while still maintaining clear internal boundaries between routes, services, repositories, and the database.

Microservices are not being introduced simply to demonstrate distributed architecture. The current product requirements do not justify the additional operational and communication complexity.

If the system develops a concrete requirement that cannot be handled cleanly within the modular monolith, the architecture can be reconsidered based on that requirement.

## 10. Technology decision principles

Technology choices for the project follow these principles:

- Choose technologies that support the actual product requirements.
- Prefer technologies that strengthen transferable engineering skills.
- Avoid adding tools purely for CV breadth or because they are currently fashionable.
- Keep the architecture simple enough to understand and operate.
- Prefer clear boundaries between presentation, business logic, persistence, and infrastructure.
- Keep security-sensitive decisions on the backend.
- Prefer technologies that can be tested and reasoned about locally.
- Introduce additional infrastructure only when a concrete requirement justifies it.

These principles are particularly important for a portfolio project because technical complexity should demonstrate engineering judgement rather than simply increase the number of technologies used.

## 11. Current implementation status

The current implementation includes:

- React and TypeScript frontend project
- Vite development tooling
- `/api/*` development proxy to FastAPI
- FastAPI application
- Python application configuration
- SQLAlchemy database engine
- SQLAlchemy domain models
- PostgreSQL database schema
- Alembic migration setup and initial migration

The following technology-related architecture is selected but not yet implemented:

- CSS Modules in the frontend
- Pydantic API schemas
- repository implementations
- database session management
- server-managed authentication sessions
- CSRF protection
- authenticated REST endpoints
- service-layer business logic

## 12. Deferred technology choices

The MVP deliberately does not introduce the following technologies or infrastructure:

- machine-learning infrastructure for matching
- a separate analytical database
- GraphQL
- WebSockets
- background job infrastructure
- microservices
- Kubernetes
- a dedicated geospatial database or PostGIS
- a mobile application framework
- a separate authentication platform

These technologies may become relevant in future versions, but they are not required to prove the core adoption workflow.

The technology stack should be reconsidered when the product requirements change, not simply because a different technology becomes available or popular.
