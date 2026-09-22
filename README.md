# Raise 'n Rescue

Raise 'n Rescue is a web-based animal adoption platform designed to help prospective adopters make more informed decisions about animal compatibility and navigate the adoption process after applying.

## Problem

Prospective adopters can struggle with two connected parts of the adoption journey:

1. Understanding which available animals may be compatible with their circumstances and lifestyle.
2. Understanding what is happening with an adoption application after it has been submitted.

Raise 'n Rescue addresses both problems through structured animal information, an adopter lifestyle profile, transparent rules-based compatibility guidance, and an application workflow with status tracking.

The system is intended to support adoption decisions, not make them. A matching result represents potential compatibility and is not an approval, rejection, reservation or guarantee that an animal is suitable.

## Primary users

### Prospective adopters

Prospective adopters can:

- browse and filter available animals;
- view detailed animal profiles;
- maintain a structured lifestyle profile;
- receive transparent potential-match results;
- save animals as favourites;
- submit adoption applications;
- track application status and history.

### Rescue staff

Rescue staff can:

- manage animals within their organisation;
- maintain animal compatibility information;
- review adoption applications;
- update application statuses;
- complete adoption workflows.

Rescue staff access is organisation-scoped so that staff members operate only on data belonging to their organisation.

## MVP scope

The MVP is focused on dogs and cats and covers the main parts of the adoption journey:

1. Animal browsing and filtering
2. Animal profiles
3. Adopter lifestyle profiles
4. Rules-based potential matching
5. Favourites
6. Adoption applications
7. Application status tracking and history
8. Basic rescue-side management
9. Authentication and adopter/rescue roles

The matching system is deterministic and explainable. It is there to help an adopter identify animals that may be compatible with their situation. It does not approve, reject or reserve an animal.

A potential match is only guidance. The final adoption decision remains with the adopter and rescue organisation.

## Deliberately deferred

These features are not part of the MVP:

- machine-learning matching;
- AI-generated animal descriptions;
- chatbot functionality;
- lost-pet functionality;
- donations and payments;
- messaging and notifications;
- maps and distance-based search;
- social features and reviews;
- advanced recommendation systems;
- additional animal species;
- complex administration and analytics;
- native mobile applications;
- microservices or Kubernetes infrastructure.

The goal is to get the core adoption workflow working properly before adding this extra complexity.

## Technology

I'm building the project as a modular monolith using:

- **Frontend:** React + TypeScript
- **Styling:** CSS Modules
- **Backend:** FastAPI + Python
- **API:** REST
- **Data access:** SQLAlchemy
- **Validation:** Pydantic
- **Database:** PostgreSQL
- **Migrations:** Alembic
- **Authentication:** server-managed sessions with secure HTTP-only cookies

I chose this stack because I want the project to focus on the engineering problems that matter for the MVP: API design, relational data modelling, authentication and authorisation, business logic, testing and maintainability.

The frontend communicates with the backend through the REST API. The backend is responsible for the business rules and security-sensitive decisions rather than relying on the frontend to enforce them.

## Repository structure

The project is currently organised into a backend, frontend, database migrations and documentation:

```text
raise-n-rescue/
|-- backend/
|   |-- app/
|       |-- api/
|       |-- core/
|       |-- models/
|       |-- repositories/
|       |-- schemas/
|       |-- security/
|       |-- services/
|
|-- frontend/
|-- migrations/
|-- docs/
|   |-- product/
|   |-- architecture/
|   |-- data/
|   |-- engineering/
|   |-- decisions/
|
|-- README.md
```

## Documentation

I split the project documentation into a few areas so that the different parts of the system are easier to find.

### Product

- docs/product/product-overview.md - what I'm building, who it's for and what the MVP covers.
- docs/product/requirements.md - the functional requirements, business rules and acceptance criteria.

### Architecture

- docs/architecture/architecture.md - how the different parts of the system fit together.
- docs/architecture/technology-decisions.md - the main technology choices made and why.
- docs/architecture/api-design.md - the REST API design and the rules around authentication, authorisation and workflows.

### Data

- docs/data/data-model.md - the database structure, relationships and important constraints.

### Engineering

- docs/engineering/testing-strategy.md - how I tested the system.
- docs/engineering/security.md - the security decisions and requirements for the application.

### Decisions

- docs/decisions/decision-log.md - the important decisions made during the project, including decisions that were later changed.

## Current implementation status

I have the initial project foundation in place:

- FastAPI backend;
- React and Vite frontend;
- PostgreSQL database;
- SQLAlchemy models;
- Alembic migrations;
- core domain enums;
- initial database schema;
- development environment configuration;
- basic backend health endpoint;
- frontend-to-backend API proxy in development.

The full MVP is not implemented yet.

Some parts of the design are therefore ahead of the code. For example, the complete authentication and session system, matching service, application workflow including snapshot persistence, full REST API and broader automated testing still need to be implemented.

I'll keep the documentation clear about what is implemented, what has been designed but not implemented yet, and what has deliberately been deferred.

## Engineering principles

A few requirements I enforced for this project:

- The backend must be responsible for business rules and security-sensitive decisions.
- The code must be separated into clear responsibilities instead of putting everything into API routes.
- The database must enforce important structural rules where it makes sense.
- The application status changes must follow defined workflows rather than allowing arbitrary changes.
- Rescue staff should only be able to access data belonging to their organisation.
- The matching system should be deterministic and explainable.
- Matching should never make the adoption decision for someone.
- Important workflows that update multiple records should be handled transactionally.
- The business logic must be testable independently from the HTTP layer.
- Authentication and session handling must be designed with security in mind from the beginning.
- The documentation must reflect the actual state of the project rather than claiming something is finished when it is not.

I'm trying to prioritise learning the underlying engineering concepts instead of adding technologies just to make the project look more complicated.

## Project status

This project is still under active development.

I've finished the initial project setup, backend structure, database models and initial migration. I'll continue working on the actual application behaviour, starting with the backend services and API.

