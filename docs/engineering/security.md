# Security

This document defines the security approach for Raise 'n Rescue, including authentication, authorisation, organisation isolation, data protection, application security, and operational considerations.

The backend is the primary security boundary. The React client can improve usability and provide client-side validation, but it must not be trusted to enforce access control or business rules.

The security design is documented alongside the current implementation status. Controls that are designed but not yet implemented are identified explicitly.

## 1. Security principles

Raise 'n Rescue follows these principles:

- enforce security-sensitive rules on the backend
- authenticate users before allowing access to protected resources
- authorise every protected operation according to the authenticated user's role and ownership
- derive organisation ownership from the authenticated session rather than trusting client-supplied organisation identifiers
- use least privilege for application and database access
- validate and constrain untrusted input
- avoid exposing sensitive information through API responses or logs
- store secrets outside source control
- use secure session handling
- preserve important workflow history for accountability
- treat security as part of normal feature implementation rather than a separate final phase

## 2. Trust boundaries

The main trust boundaries are:

### Browser to API

The browser is an untrusted client. Requests can be modified by the user or by an attacker, so the backend must independently validate authentication, authorisation, ownership, and business rules.

The React application must not be treated as a trusted source for user role, organisation ownership, application status, animal ownership, or other protected fields.

### API to database

The backend communicates with PostgreSQL through SQLAlchemy and the configured database connection.

The database provides structural integrity through primary keys, foreign keys, unique constraints, check constraints, and enum types.

Application services remain responsible for contextual business rules that cannot be represented safely as simple database constraints.

### Rescue organisation boundary

Rescue staff accounts belong to a specific rescue organisation.

Authenticated rescue operations must be scoped to that organisation. A user from one organisation must not be able to access or modify another organisation's animals, facilities, applications, or other organisation-owned records.

Organisation isolation is enforced by backend services and repositories rather than by filtering data only in the frontend.

## 3. Authentication

Authentication establishes which user is making a request.

The intended MVP authentication model uses server-managed sessions rather than storing authentication tokens in browser local storage.

The authentication flow is:

1. The user submits credentials to the backend.
2. The backend validates the credentials.
3. The backend creates a server-side authenticated session.
4. The backend sends a session identifier to the browser in an HTTP-only cookie.
5. Protected requests use that cookie to identify the authenticated session.
6. The backend resolves the authenticated user and applies authorisation rules.
7. Logout invalidates the server-side session and clears the browser cookie.

The browser therefore does not need access to the session identifier through JavaScript.

## 4. Password security

Passwords must never be stored in plaintext.

The backend will store a password hash and will verify submitted passwords against that hash during authentication.

The specific password-hashing library and algorithm will be selected and configured during authentication implementation. The project documentation does not treat an algorithm as implemented until it is present in the application.

Authentication failures should use generic error responses so that the API does not unnecessarily reveal whether an email address exists.

Password values must not be written to application logs, error messages, test output, or API responses.

## 5. Session security

The session cookie should use security-focused attributes appropriate to the deployment environment:

- `HttpOnly` to prevent JavaScript from reading the session identifier
- `Secure` when served over HTTPS
- an appropriate `SameSite` policy
- a limited session lifetime

The server must treat the session as the source of authenticated identity rather than trusting identity information supplied by the client.

Logout must invalidate the server-side session so that a previously authenticated session cannot continue to be used.

Session management is part of the intended authentication architecture but is not yet implemented in the current application.

## 6. Cross-site request forgery protection

Because authentication uses cookies, the application must protect state-changing requests against cross-site request forgery (CSRF).

CSRF protection is required for authenticated state-changing operations such as profile updates, favourites, application submission, status changes, and adoption completion.

The exact CSRF mechanism will be selected during authentication implementation and must be tested as part of the security test suite.

## 7. Authorisation

Authentication answers who the user is. Authorisation determines what that user is allowed to do.

Authorisation must be enforced by the backend for every protected operation.

The backend must not trust client-supplied values for role, user identity, organisation ownership, application status, or other security-sensitive fields.

Adopter permissions are scoped to the authenticated adopter and their own data. An adopter may access or modify their own lifestyle profile, favourites, and applications according to the application workflow rules.

Rescue staff permissions are scoped to the rescue organisation associated with their authenticated account. Rescue staff may manage organisation-owned animals, facilities, and applications within that organisation according to their role permissions.

A request that does not satisfy the required role or ownership rules must be rejected by the backend.

## 8. Organisation isolation

Each rescue staff account belongs to one rescue organisation.

For authenticated rescue requests, the backend derives the organisation from the authenticated user rather than accepting an organisation identifier as an authority from the client.

Repositories and services must apply organisation scoping when accessing organisation-owned records.

This applies to resources including:

- animals
- facilities
- applications
- organisation information

Organisation isolation must apply to both read and write operations. A user must not be able to bypass isolation by modifying an identifier in an API request.

The database foreign keys provide structural relationships between organisations and their records, while application services and repositories enforce the authenticated organisation boundary.

## 9. Rescue staff onboarding

Rescue staff accounts are created through controlled organisation invitations rather than unrestricted public registration.

An invitation is associated with a specific organisation and role and contains a one-time, time-limited invitation token.

The database stores a hash of the invitation token rather than the raw token.

An invitation must be checked for:

- valid organisation association
- intended role
- expiry
- whether it has already been used

A successfully accepted invitation must not be reusable.

Raw invitation tokens must not be written to application logs or persisted as plaintext.

The current database model contains the organisation invitation structure, but the complete invitation acceptance workflow is not yet implemented.

## 10. Input validation

All data received from the browser must be treated as untrusted input.

The API will validate request data using Pydantic schemas before passing it into application services.

Validation should enforce the expected data type, required fields, allowed values, length limits, and other relevant constraints.

Business rules that depend on database state must still be checked by the service layer after request validation. Passing schema validation does not make a request authorised or valid for the current application state.

Database queries should use SQLAlchemy parameters and ORM query construction rather than constructing SQL statements by concatenating untrusted input.

Client-side validation may improve the user experience, but it must never replace backend validation.

## 11. API error handling

API errors should provide enough information for the client to handle the failure without exposing unnecessary internal details.

The API should avoid returning database errors, stack traces, SQL statements, passwords, session identifiers, invitation tokens, or other internal security information to users.

Authentication and authorisation failures should not reveal more information than necessary.

Unexpected internal errors should be logged appropriately on the server while returning a controlled response to the client.

## 12. Data exposure

API responses should contain only the information required by the requesting user and the requested operation.

Public animal information can be exposed through the public animal endpoints, but private adopter information must not be exposed through those endpoints.

Adopter application data should only be accessible to the relevant adopter and authorised rescue staff within the organisation responsible for the animal.

Sensitive authentication data such as password hashes, session data, and invitation token hashes must not be returned through normal API responses.

The backend must enforce these boundaries even if the frontend does not display the protected information.

## 13. Secrets and configuration

Secrets and environment-specific configuration must remain outside source-controlled application code.

The project currently uses a root `.env` file for local database configuration. The file is excluded from Git through `.gitignore`.

The repository contains an `.env.example` file that documents the expected configuration fields without containing the real database password.

Database credentials, session secrets, API keys, and similar values must not be committed to the repository.

Production secrets should be supplied through the deployment environment or an appropriate secret-management mechanism rather than being hard-coded into the application.

The application database user should have only the permissions required by the application and its operational workflows.

## 14. Database security and integrity

PostgreSQL is responsible for enforcing structural data integrity through primary keys, foreign keys, unique constraints, check constraints, and enum types.

The application must not rely on the frontend to maintain database integrity.

Multi-record operations that must succeed or fail together should run inside database transactions. This is particularly important for application submission, application status changes, and adoption completion.

Database migrations are managed through Alembic so that schema changes are explicit and reproducible.

The application database account should use the minimum permissions required for normal application operation.

Production database backups and restore procedures are operational concerns that must be established before production deployment. They are not part of the current local development implementation.

## 15. Logging and sensitive information

Application logging should support troubleshooting and security investigation without exposing sensitive information.

The application must not log:

- passwords
- password hashes
- session identifiers
- invitation tokens
- invitation token hashes
- database credentials
- unnecessary private applicant information

Authentication failures, authorisation failures, unexpected errors, and important workflow events may be logged when doing so is useful for security or operational investigation.

Logs should contain enough context to investigate an event without unnecessarily storing personal or security-sensitive data.

## 16. Browser and application security

The React frontend should avoid introducing client-side injection vulnerabilities by relying on React's normal escaping behaviour and avoiding unsafe HTML rendering unless there is a justified and controlled use case.

The application should use appropriate security-related HTTP response headers in production.

The production deployment must use HTTPS so that authentication cookies and other sensitive traffic are protected in transit.

The exact production header configuration will be established as part of deployment hardening and is not currently implemented.

## 17. Dependency security

Application dependencies should be kept at known versions and reviewed periodically for security vulnerabilities and incompatible updates.

Dependency updates should be tested before being incorporated into the project.

The current project records its Python dependencies and frontend package dependencies in the project dependency files. Dependency security monitoring and automated vulnerability scanning are not yet implemented as a dedicated project control.

## 18. Abuse and availability controls

Authentication, invitation, and other security-sensitive endpoints may require rate limiting or similar abuse controls before production deployment.

Rate limiting is not currently implemented in the MVP foundation.

When these controls are introduced, they should be applied at an appropriate layer and tested so that legitimate users can still complete normal workflows.

## 19. File and image handling

Animal profiles may eventually include uploaded or externally stored photos.

When file uploads are implemented, uploaded content must be treated as untrusted input.

The upload workflow should validate file type and size, use safe generated filenames or object identifiers, and prevent path traversal or arbitrary filesystem access.

Uploaded files should not be stored in a location where user-controlled paths can execute application code.

The final storage and processing approach will be selected when the photo upload workflow is implemented.

The current MVP foundation stores animal photo URLs but does not implement a user-facing file upload workflow.

## 20. Security testing

Security-sensitive behaviour must be covered by automated tests where practical.

The security test suite should verify authentication, authorisation, ownership boundaries, organisation isolation, session handling, invitation rules, input validation, and protection of sensitive information.

Important scenarios include:

- unauthenticated access to protected endpoints is rejected
- adopters cannot access another adopter's private data
- adopters cannot perform rescue-staff operations
- rescue staff cannot access another organisation's resources
- client-supplied organisation identifiers cannot bypass organisation isolation
- invalid or expired invitations are rejected
- used invitations cannot be reused
- logout invalidates the authenticated session
- protected state-changing requests enforce CSRF protection once cookie authentication is implemented
- sensitive credentials and tokens are not exposed in API responses
- invalid input is rejected by the backend

These tests complement the broader testing strategy documented in `docs/engineering/testing-strategy.md`.

## 21. Implementation status

The current implementation provides part of the security foundation, but the complete security architecture is not yet implemented.

Currently implemented:

- database configuration is loaded from environment configuration
- the local `.env` file is excluded from Git
- database relationships use foreign keys
- role and organisation relationships are represented in the data model
- the user model constrains adopter and rescue-staff organisation membership
- organisation invitations store a token hash rather than a raw token
- invitation records include expiry and used-state fields

Designed but not yet implemented:

- password hashing and credential verification
- server-managed authentication sessions
- secure HTTP-only session cookies
- logout and server-side session invalidation
- CSRF protection
- endpoint-level authentication and authorisation
- organisation-scoped service and repository access
- complete rescue invitation acceptance workflow
- security-focused API error handling
- production HTTPS and security headers
- rate limiting and other abuse controls
- automated security tests

The security design should therefore be treated as the target architecture until these controls are implemented and verified.

## 22. Related documentation

Security decisions are connected to the rest of the project architecture:

- `docs/architecture/architecture.md` - authentication, authorisation, organisation isolation, and system boundaries
- `docs/architecture/api-design.md` - protected API operations and endpoint boundaries
- `docs/data/data-model.md` - users, organisations, invitations, and database integrity
- `docs/engineering/testing-strategy.md` - security and authorisation testing requirements
- `docs/decisions/decision-log.md` - significant project and technology decisions
