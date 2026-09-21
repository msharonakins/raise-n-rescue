# Decision log

This document records significant decisions that changed or clarified the direction of Raise 'n Rescue.

It is a historical record rather than the source of truth for the current architecture. Current technology choices are documented in `docs/architecture/technology-decisions.md`.

## 1. Project selection

**Date:** 2026-09-11

**Decision:** Select Raise 'n Rescue as Portfolio Project #1.

### Alternatives considered

- Residence Maintenance Request System
- Volunteer Shift Management System
- Easy Eats
- Raise 'n Rescue

### Reasoning

Raise 'n Rescue provided the strongest overall combination of portfolio value and engineering depth for the project goals. It gives me room to demonstrate:

- authentication and authorisation
- relational database design
- realistic application workflows
- backend business rules
- deterministic matching logic
- frontend and UI/UX work
- security considerations
- meaningful testing

The project also addresses a real-world problem rather than being only a technical demonstration.

The decision was based on the balance between technical depth, product design, realistic workflows, and the opportunity to demonstrate complete software-engineering skills.

## 2. MVP scope lock

**Date:** 2026-09-11

**Decision:** Lock the MVP around the core adoption journey for dogs and cats.

### Included capabilities

- animal browsing, filtering, and profiles
- adopter lifestyle profiles
- deterministic potential matching
- favourites
- adoption applications
- application status tracking and history
- basic rescue-side application and animal management
- authentication and role-based access
- controlled rescue organisation onboarding

### Deferred capabilities

- machine-learning matching
- AI-generated animal descriptions or chatbot functionality
- lost-pet functionality
- donations and payments
- messaging and notifications
- maps and geospatial discovery
- social features
- additional animal species
- advanced analytics
- mobile applications
- microservices or Kubernetes

### Reasoning

The scope was deliberately constrained so the project could demonstrate a complete adoption workflow rather than spreading effort across too many features.

The MVP needs enough complexity to demonstrate real engineering decisions, but additional infrastructure and features should only be introduced when they solve a demonstrated product or technical requirement.

Matching was kept deterministic and explainable for the MVP. Machine learning was deferred until there is real structured data and adoption-outcome data that could justify it.

## 3. Initial technology stack proposal

**Date:** 2026-09-11

**Decision:** Initially propose React + TypeScript + CSS for the frontend, Spring Boot + Java 21 for the backend, PostgreSQL for the database, and REST for the API.

### Alternatives considered

- FastAPI + Python
- Flutter Web
- Firebase
- GraphQL

### Reasoning

Spring Boot and Java were initially selected because I already had some Java experience and the stack is widely used in professional backend development.

The initial architecture also used secure server-managed cookie/session authentication rather than storing authentication tokens in browser local storage.

Firebase and GraphQL were not selected as core parts of the architecture because the project benefits from explicit backend business logic, relational data modelling, and a conventional REST API.

This was an initial proposal rather than a permanent commitment.

## 4. Backend stack reversal

**Date:** 2026-09-13

**Decision:** Replace the planned Spring Boot + Java backend with FastAPI + Python.

### Previous direction

The backend was originally planned around Spring Boot and Java 21.

### Final direction

The backend uses:

- FastAPI
- Python
- SQLAlchemy
- Pydantic
- PostgreSQL
- Alembic
- REST

The frontend remains React + TypeScript with CSS Modules.

### Reasoning

The change was made because of the project's time constraints and my existing practical experience with Python. Continuing with Spring Boot would have added a significant framework-learning burden that was not necessary to demonstrate the engineering concepts the project is intended to show.

Using FastAPI allows more of the available project time to go towards API design, architecture, relational modelling, authentication, authorisation, business rules, testing, deployment, and security.

The choice also keeps the backend aligned with my broader interest in Python-based data and AI work without forcing those technologies into the MVP.

This decision was made for the needs of this project rather than for perceived CV value. Spring Boot and Java remain useful technologies to learn for future work, but they are not being included in this project solely to demonstrate technology breadth.

### Consequence

The current architecture and implementation use FastAPI + Python. The earlier Spring Boot proposal is retained here only as historical context and must not be treated as the current backend stack.

## 5. How decisions are recorded

The decision log is intended to preserve significant project decisions and changes in direction.

A decision belongs in this document when it materially affects the product scope, architecture, technology direction, or engineering approach.

Current decisions should be documented in the appropriate canonical document as well:

- product scope and requirements belong in `docs/product/`
- current architecture belongs in `docs/architecture/architecture.md`
- current technology choices belong in `docs/architecture/technology-decisions.md`
- API contracts belong in `docs/architecture/api-design.md`
- data-model decisions belong in `docs/data/data-model.md`

When a previous decision is changed, the historical decision remains in this log while the current documentation is updated to reflect the new direction.

This keeps the project's history visible without allowing outdated decisions to be mistaken for the current implementation.
