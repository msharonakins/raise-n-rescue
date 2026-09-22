# Architecture

## 1. Architecture overview

Raise 'n Rescue uses a modular monolith architecture for the MVP.

The system is divided into a React frontend, a FastAPI backend, and a PostgreSQL database. The frontend communicates with the backend through a REST API.

The backend is responsible for authentication, authorisation, validation, business rules, matching logic, application workflows, and database access.

The main architectural boundaries are:

- **Frontend:** presentation, user interaction, client-side state, API communication, and user-facing validation.
- **API routes:** HTTP concerns such as request parsing, authentication dependencies, response formatting, and status codes.
- **Services:** application and domain logic, including matching, application workflows, authorisation rules, and state transitions.
- **Repositories:** database access and persistence operations.
- **Database:** relational data storage and structural integrity constraints.

The backend is authoritative for business rules and security. The frontend must not make decisions that affect whether an operation is allowed or whether an adoption workflow can proceed.

## 2. System context

The system consists of three primary components.

### Frontend

The frontend is a React application written in TypeScript. It provides the user interface for prospective adopters and rescue staff.

The frontend communicates with the backend through `/api/*` endpoints.

During development, the Vite development server runs separately from FastAPI and proxies `/api/*` requests to the backend.

### Backend

The backend is a FastAPI application written in Python.

It exposes the REST API and contains the application's business logic. It is responsible for enforcing authentication, authorisation, validation, matching rules, application state transitions, and other domain rules.

The backend communicates directly with PostgreSQL through SQLAlchemy.

### Database

PostgreSQL is the system's relational database.

It stores users, rescue organisations, facilities, animals, adopter profiles, favourites, applications, application status history, and related structured data.

Database constraints are used to enforce structural rules such as foreign keys, uniqueness, non-negative values, and valid relationships between records. Business decisions remain the responsibility of the backend application.

### Communication flow

The normal request flow is:

```text
React frontend
      |
      | HTTP / REST
      v
FastAPI backend
      |
      | SQLAlchemy
      v
PostgreSQL
```

The backend remains the authority between the user interface and the database. The frontend does not communicate directly with PostgreSQL.

## 3. Frontend architecture

The frontend is responsible for presenting the application and handling user interaction. It should remain relatively thin in terms of business logic.

The frontend is responsible for:

- rendering pages and reusable UI components
- collecting and displaying user input
- managing client-side UI state
- managing API request state such as loading and error states
- performing immediate client-side validation where useful for user experience
- displaying backend validation and business-rule errors
- presenting animal information, matching results, favourites, and application information
- handling responsive layouts and accessibility
- communicating with the backend through the REST API

The backend remains authoritative for all security-sensitive and business-critical decisions.

For example, the frontend may display a potential match based on the response from the matching API, but it must not independently calculate whether an animal qualifies as a potential match.

### Same-origin application structure

The intended deployment structure is:

```text
Browser
   |
   v
Web server / reverse proxy
   |--------------------> React frontend
   |
   `--------------------> FastAPI /api/*
```

The frontend is served at the application's main origin, while API requests use the `/api/*` path.

This same-origin arrangement reduces unnecessary cross-origin configuration and works well with the planned HTTP-only session cookie authentication model.

### Frontend styling

The frontend is intended to use CSS Modules for component-level styling.

The UI is treated as part of the engineering design rather than as a separate cosmetic layer. Layout, accessibility, responsive behaviour, loading states, validation feedback, empty states, and error handling are all part of the frontend's responsibilities.

## 4. Backend architecture

The backend follows a layered structure that separates HTTP handling, application and domain logic, database access, and persistence.

The intended request flow is:

```text
API route
    |
    v
Service
    |
    v
Repository
    |
    v
Database
```

The layers have separate responsibilities so that business rules do not become tightly coupled to HTTP handlers or database queries.

### 4.1 Routes

API routes handle HTTP-specific concerns.

Routes are responsible for:

- receiving HTTP requests
- validating request data through Pydantic schemas
- obtaining the authenticated user where required
- calling the appropriate service
- returning the appropriate HTTP response
- translating expected application errors into API responses

Routes should remain thin. They should not contain the main business rules for matching, application workflows, authorisation, or adoption state transitions.

### 4.2 Services

Services contain the application and domain logic of the system.

Services are responsible for rules and workflows such as:

- authentication and account workflows
- authorisation checks
- animal availability rules
- deterministic matching
- favourite management
- application submission and validation
- application status transitions
- adoption completion
- rescue organisation ownership checks
- multi-record transactional workflows

Services may coordinate multiple repository operations when a business operation affects more than one entity.

Business rules should live in services rather than in API routes or frontend code. This keeps the rules independently testable and prevents different API endpoints from implementing conflicting versions of the same rule.

The service layer is an architectural boundary established for the application. Most of these services are not implemented yet.

### 4.3 Repositories

Repositories handle database access and persistence operations.

Repositories are responsible for tasks such as:

- querying records
- loading related data needed by a service
- creating and updating records
- deleting records where deletion is part of the allowed workflow
- applying repository-level query scoping such as organisation ownership

Repositories should not contain the main business decisions of the application. A repository can retrieve an animal, application, or organisation record, but the service layer determines whether the requested operation is permitted and what business rules apply.

Repositories provide a consistent database-access boundary for services and help keep database queries separate from application logic.

The repository layer is an architectural boundary established for the application. The repository implementations are not in place yet.

### 4.4 Database

PostgreSQL is the persistent data store for the application.

SQLAlchemy provides the Python persistence layer used by the backend to communicate with PostgreSQL. Alembic manages versioned database schema migrations.

The database is responsible for structural integrity rules such as:

- primary keys
- foreign keys
- unique constraints and indexes
- non-negative value constraints where required
- required and optional fields
- valid relationships between tables

The database also uses PostgreSQL enum types for stable domain values such as user roles, animal statuses, application statuses, and other controlled values.

Database constraints protect the integrity of persisted data, but they do not replace application-level business rules. Rules such as whether an animal can be applied for, whether an application status transition is valid, or whether a rescue staff member may access a record belong in the backend service layer.

The current implementation includes the SQLAlchemy database engine, the SQLAlchemy models, and the initial Alembic migration. Database session management and the application repository layer are part of the planned backend architecture and are not implemented yet.

## 5. Authentication and session architecture

Raise 'n Rescue is designed to use server-managed session authentication rather than storing authentication tokens in browser local storage.

The intended authentication flow is:

1. The user submits their credentials to the login endpoint.
2. The backend validates the credentials and verifies the stored password hash.
3. The backend creates a server-side authenticated session.
4. The backend sends a secure HTTP-only session cookie to the browser.
5. Subsequent authenticated requests use the session cookie to identify the user.
6. The backend loads the authenticated user and applies the required role and organisation checks.
7. Logout invalidates the server-side session and clears the browser cookie.

The browser should not store authentication tokens in local storage. Authentication state is controlled by the backend and represented to the browser through the session cookie.

The session cookie is intended to use security properties including HttpOnly, Secure when HTTPS is used, an appropriate SameSite policy, and a limited lifetime.

CSRF protection is required because authentication is based on a browser cookie. The exact CSRF mechanism will be defined during implementation.

A dedicated sessions table is part of the planned security design. It is not part of the current database schema yet.

Authentication and session management are designed but are not implemented yet. The current backend only exposes the health endpoint and does not yet provide login, logout, registration, session validation, or authenticated API access.

## 6. Authorisation and organisation isolation

Authorisation is enforced by the backend after the authenticated user has been identified.

Raise 'n Rescue has two application roles:

- **Adopter:** can manage their own adopter profile, favourites, and applications.
- **Rescue staff:** can manage animals, facilities, and applications belonging to their rescue organisation.

A rescue staff account belongs to one rescue organisation. The organisation associated with the authenticated user is determined by the backend rather than being supplied as a trusted value by the client.

Rescue staff operations must be scoped to the authenticated user's organisation. Services and repositories must prevent a rescue staff member from reading or modifying records belonging to another organisation.

Organisation ownership is therefore part of the security boundary, not just a filtering convenience.

The API uses the following general authorisation distinction:

- **403 Forbidden:** the user has the required authentication but does not have the required role for the operation.
- **404 Not Found:** a resource exists outside the user's permitted ownership boundary and should not be exposed through the API.

Rescue staff accounts are not created through unrestricted public registration. The intended onboarding flow uses organisation-specific invitations that establish the organisation and role before the staff member activates their account.

Cross-organisation access must be prevented at the backend service and repository boundaries. The frontend must not be relied upon to hide records that a user is not authorised to access.

The authorisation and organisation-isolation design is established, but the corresponding authentication dependencies, services, repository scoping, and invitation workflow are not implemented yet.

## 7. Matching architecture

The matching system is designed as deterministic, rules-based decision support in the backend service layer.

The matching engine evaluates structured information from the adopter's current lifestyle profile against structured information about available animals.

The matching process is designed around two types of rules:

- **Hard constraints:** conditions that can make an animal incompatible with the adopter's stated circumstances.
- **Soft factors:** characteristics that contribute positively or negatively to the compatibility score without automatically excluding an animal.

The matching service returns an explainable result rather than an opaque recommendation. The response can include the compatibility level, score, and reasons contributing to the result.

The MVP uses the following compatibility levels:

- **Potential match**
- **Strong potential match**

The matching engine must not make the adoption decision. It must not automatically approve, reject, reserve, or otherwise remove an animal from consideration based on its result.

Animals outside the match results remain available for normal browsing and discovery. A lack of matching results should not prevent an adopter from viewing available animals or submitting an application where the application rules allow it.

Unknown animal compatibility values must not automatically be treated as compatible. The matching rules must handle unknown information explicitly.

Rescue staff are responsible for maintaining the structured animal information used by the matching system. The matching service then applies the same rules consistently to the supplied inputs.

For identical inputs and the same matching rules, the matching service should produce the same result. This makes the logic deterministic and independently testable.

The matching engine belongs in the backend service or domain layer so that it can be tested independently from HTTP routes and reused by different application workflows.

The matching architecture is designed but the matching service and API are not implemented yet.

## 8. Application workflow architecture

Applications are managed through an explicit state machine. The backend service layer is responsible for validating and applying status transitions.

The valid application states are:

- SUBMITTED
- UNDER_REVIEW
- HOME_CHECK
- APPROVED
- ADOPTED
- DECLINED
- WITHDRAWN
- CLOSED_ANIMAL_ADOPTED

The intended transitions are:

- SUBMITTED -> UNDER_REVIEW
- SUBMITTED -> WITHDRAWN
- SUBMITTED -> DECLINED
- SUBMITTED -> CLOSED_ANIMAL_ADOPTED
- UNDER_REVIEW -> HOME_CHECK
- UNDER_REVIEW -> WITHDRAWN
- UNDER_REVIEW -> DECLINED
- UNDER_REVIEW -> CLOSED_ANIMAL_ADOPTED
- HOME_CHECK -> APPROVED
- HOME_CHECK -> WITHDRAWN
- HOME_CHECK -> DECLINED
- HOME_CHECK -> CLOSED_ANIMAL_ADOPTED
- APPROVED -> ADOPTED
- APPROVED -> WITHDRAWN

ADOPTED, DECLINED, WITHDRAWN, and CLOSED_ANIMAL_ADOPTED are terminal states.

Every successful status transition should create an application status-history record containing the new status, the time of the change, the actor responsible for the change, and an optional reason.

Application submission uses the adopter's current lifestyle profile to validate that the profile is complete and to capture the relevant profile information at the time of submission.

The submitted application preserves an immutable snapshot of the relevant adopter information used for the application. Later changes to the adopter's profile must not rewrite the historical application record.

Matching continues to use the adopter's current lifestyle profile. It is not based on an old application snapshot.

The application workflow must be enforced by the backend service layer. The frontend may display available actions based on the current status, but it must not be trusted to enforce valid transitions.

The application state machine and snapshot behaviour are designed but the application services, API endpoints, and complete workflow enforcement are not implemented yet.

The current database model now contains the status-history actor field and the required scalar application snapshot fields described by this design. The application services, API endpoints, and complete workflow enforcement are still not implemented.

## 9. Transactional workflows

Some operations affect multiple related records and must be completed as a single database transaction.

The service layer is responsible for coordinating these workflows, while the database transaction ensures that either all required changes are committed or none of them are.

### 9.1 Application submission

Application submission is designed to follow this general sequence:

1. Authenticate the requester.
2. Confirm that the requester has the adopter role.
3. Validate the submitted application data.
4. Load the selected animal and confirm that it is currently available.
5. Check that the adopter does not already have an active application for the same animal.
6. Load the adopter's current lifestyle profile and confirm that it is complete.
7. Begin the database transaction.
8. Create the application record.
9. Store the relevant adopter profile snapshot with the application.
10. Create the initial SUBMITTED status-history record.
11. Commit the transaction.

The availability and duplicate-application checks must be re-evaluated as part of the transactional workflow so that concurrent requests cannot bypass the application rules.

The data model is intended to enforce one active application per adopter and animal through a database constraint in addition to the service-level validation.

The current migration implements the planned partial unique index for active applications. The application service must still handle the resulting database constraint safely when concurrent submissions occur.

### 9.2 Adoption completion

Completing an adoption is also a multi-record transactional workflow.

The intended sequence is:

1. Confirm that the rescue staff member is authorised for the animal's organisation.
2. Confirm that the selected application is eligible for adoption completion.
3. Mark the successful application as ADOPTED.
4. Mark the animal as ADOPTED.
5. Move other active applications for the same animal to CLOSED_ANIMAL_ADOPTED.
6. Create the required status-history records for the affected applications.
7. Commit the transaction.

After adoption completion, the animal must no longer be available for new applications.

The transaction ensures that the animal status and application statuses cannot be left in an inconsistent partial state if an error occurs during the workflow.

The transactional workflows are designed but the corresponding application and adoption services are not implemented yet.

## 10. Responsibility boundaries

The main responsibilities of each architectural layer are summarised below.

| Layer | Primary responsibility | Should not own |
| --- | --- | --- |
| Frontend | UI, user interaction, client-side state, API communication, and immediate user-facing validation | Authorisation, business-rule enforcement, database access, or final workflow decisions |
| API routes | HTTP request handling, schema validation, authentication dependencies, service calls, and HTTP responses | Core business rules or direct database workflows |
| Services | Business rules, domain workflows, authorisation decisions, matching, state transitions, and transaction coordination | UI concerns or low-level database query implementation |
| Repositories | Database queries and persistence operations | Business decisions or HTTP concerns |
| Database | Persistent storage and structural data integrity | Application-level workflow decisions or authorisation |

These boundaries are intended to keep the system understandable and testable as functionality grows.

A business rule should have one authoritative implementation. If the same rule is needed by multiple routes or workflows, it should normally be implemented in a service or domain component rather than duplicated across API handlers.

Security-sensitive decisions must remain on the backend even when the frontend provides corresponding user-interface behaviour.

## 11. Architectural principles

The following principles guide the implementation of Raise 'n Rescue:

- **Backend authority:** business rules and security decisions are enforced by the backend.
- **Clear responsibilities:** each architectural layer has a defined responsibility and should avoid taking over concerns belonging to another layer.
- **Database integrity:** structural data rules are enforced at the database level where appropriate.
- **Explicit workflows:** application and adoption state changes follow defined transitions rather than arbitrary status updates.
- **Organisation isolation:** rescue staff access is scoped to their organisation and enforced server-side.
- **Deterministic matching:** MVP matching uses explicit rules that produce explainable and repeatable results.
- **Decision support only:** matching assists adopters and does not make adoption decisions.
- **Transactional consistency:** workflows that modify multiple related records use database transactions.
- **Testable business logic:** important business rules should be independently testable without requiring the HTTP layer.
- **Security-minded authentication:** authentication and session handling should use secure server-managed mechanisms appropriate for a browser application.
- **Documentation reflects reality:** architectural documentation distinguishes implemented functionality from designed functionality and deferred work.
- **Avoid unnecessary complexity:** the project should use the simplest architecture that satisfies its current requirements and introduce additional infrastructure only when there is a clear engineering reason.

## 12. Implementation status

This document describes both the intended architecture and the current implementation. The implementation status below is the source of truth for what is currently working.

### Implemented

- FastAPI application and health endpoint
- application configuration loaded from environment settings
- SQLAlchemy database engine
- SQLAlchemy domain models
- PostgreSQL database schema
- Alembic database migrations
- React and TypeScript frontend project
- Vite development server and `/api/*` proxy configuration

### Designed but not implemented

- API routes beyond the health endpoint
- Pydantic request and response schemas
- service-layer business logic
- repository implementations
- authentication and server-managed sessions
- CSRF protection
- role-based authorisation and organisation-scoped access enforcement
- rescue organisation invitation workflow
- deterministic matching service and matching API
- favourites workflow
- application submission workflow
- application status transition workflow
- adoption completion workflow
- application snapshot persistence
- frontend application features and user workflows

### Implementation alignment still required

Several parts of the current database implementation need to be brought into alignment with the intended application design before the corresponding workflows are implemented.

- The active-application uniqueness rule is implemented as a partial unique index in the current migration. The application service must still handle the resulting constraint safely during concurrent submissions.
- Application status history is implemented with an actor field, status, note, and creation timestamp. The application service must still ensure that history entries are created consistently for valid status transitions.
- The application model contains the required scalar profile snapshot fields. The application submission service must still populate these fields from the adopter's profile and preserve the snapshot as historical data.
- Application preference tables exist and can support snapshot data, but the submission service must populate them from the adopter's profile and preserve them as historical data.
- The current favourites model uses `adopter_profile_id`, while earlier design material used `adopter_id`; the implementation should use one consistent identifier convention.

These differences are implementation gaps rather than reasons to weaken the intended design. They should be resolved through deliberate schema and code changes before the affected workflows are considered complete.

### Deferred

The following areas are intentionally outside the MVP architecture:

- machine-learning-based matching
- AI-generated animal descriptions or chatbot functionality
- lost-pet functionality
- donations and payment processing
- messaging and notification infrastructure
- maps and full geospatial discovery
- social features
- additional animal species beyond dogs and cats
- advanced analytics and administration
- mobile applications
- microservices and Kubernetes
- complex recommendation infrastructure

The project will remain a modular monolith unless future requirements provide a clear reason to introduce additional architectural complexity.
