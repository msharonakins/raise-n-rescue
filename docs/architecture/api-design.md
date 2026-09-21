# API design

This document defines the REST API design for Raise 'n Rescue.

The API is the boundary between the React frontend and the FastAPI backend. The backend is authoritative for authentication, authorisation, validation, business rules, matching, application workflows, and data integrity.

The API design describes the intended contract. It should be read together with `requirements.md`, `architecture.md`, and `data-model.md`.

## 1. API principles

- The frontend communicates with the backend through the REST API.
- The frontend never accesses PostgreSQL directly.
- The backend is authoritative for business rules and security-sensitive decisions.
- API routes handle HTTP concerns and delegate business logic to services.
- Services enforce application and domain rules.
- Repositories handle database access.
- Authenticated identity and organisation ownership are derived from the server-side session rather than trusted client-provided identifiers.
- The API validates input at the request boundary, in the service layer where business rules apply, and through database constraints where structural integrity is required.
- Multi-record workflows are executed transactionally.
- API responses should expose only data the authenticated user is authorised to access.

## 2. API structure

The API uses the `/api/*` path.

The intended endpoint groups are:

| Area | Purpose |
| --- | --- |
| Authentication | Registration, login, logout, and the current authenticated user |
| Animals | Public discovery and rescue-side animal management |
| Adopter profile | The authenticated adopter's lifestyle profile |
| Matching | Potential-match results based on the current adopter profile |
| Favourites | The authenticated adopter's saved animals |
| Applications | Adoption application submission and tracking |
| Rescue applications | Rescue-side application review and status management |
| Organisations | Rescue organisation management |
| Facilities | Facilities belonging to rescue organisations |

The API follows a resource-oriented structure, but workflows that represent explicit domain actions use dedicated action endpoints where that makes the business operation clearer.

## 3. Authentication endpoints

### 3.1 Register adopter

**POST** `/api/auth/register`

Creates an adopter account.

The public registration endpoint creates `ADOPTER` accounts only. Rescue staff accounts are created through the controlled organisation invitation workflow rather than through public registration.

The request contains the credentials required to create the account. The client does not provide the user role or rescue organisation.

On successful registration, the backend creates the user account and establishes the appropriate authenticated session according to the authentication design.

### 3.2 Login

**POST** `/api/auth/login`

Authenticates a user using their credentials.

The backend validates the credentials, creates a server-side session, and returns an HTTP-only session cookie.

Invalid credentials should result in a generic authentication error rather than revealing whether an account exists.

### 3.3 Logout

**POST** `/api/auth/logout`

Invalidates the current server-side session and clears the browser authentication cookie.

### 3.4 Current user

**GET** `/api/auth/me`

Returns information about the currently authenticated user and their role.

The backend derives the authenticated user from the session rather than accepting a user ID from the client.

Unauthenticated requests receive an authentication error.

## 4. Animal endpoints

### 4.1 Public animal discovery

**GET** `/api/animals`

Returns animals that are eligible for public discovery.

The endpoint supports filtering by structured animal attributes such as:

- species
- sex
- size
- age
- energy level
- compatibility with children
- compatibility with dogs
- compatibility with cats
- suitable home type
- outdoor space requirement
- experience requirement
- facility or textual location information

Location filtering is based on the stored facility or textual location information in the MVP. The API does not perform radius, distance, coordinate, or geospatial filtering.

Discovery results exclude animals that are no longer available for adoption. The exact visibility rules for unavailable animals outside the discovery workflow remain subject to the product requirements.

List responses should contain summary information suitable for browsing. Detailed animal information is provided by the animal detail endpoint.

### 4.2 Animal detail

**GET** `/api/animals/{animal_id}`

Returns the public profile for a specific animal.

The response may include the animal's descriptive information, compatibility information, facility information, personality traits, and photos.

An animal may remain directly viewable after it is no longer available for discovery so that existing application or favourite references can still be understood, subject to the product's visibility rules.

### 4.3 Rescue animal inventory

**GET** `/api/rescue/animals`

Returns animals belonging to facilities managed by the authenticated rescue organisation.

The backend derives the organisation from the authenticated rescue staff session. The client does not provide an organisation ID to select another organisation's inventory.

### 4.4 Create animal

**POST** `/api/animals`

Creates an animal record for an authenticated rescue staff user.

The service verifies that the selected facility belongs to the authenticated user's organisation before creating the animal.

### 4.5 Update animal

**PATCH** `/api/animals/{animal_id}`

Updates an animal managed by the authenticated rescue organisation.

The service verifies organisation ownership before applying the update.

If `age_recorded_at` is used to record when the animal's age information was assessed, it should only be changed when the recorded age information changes.

## 5. Adopter profile endpoints

### 5.1 Get current profile

**GET** `/api/me/profile`

Returns the authenticated adopter's current lifestyle profile.

The backend identifies the adopter from the authenticated session.

### 5.2 Replace current profile

**PUT** `/api/me/profile`

Replaces the authenticated adopter's lifestyle profile.

The profile contains the structured information used by the matching system, including home type, outdoor space, activity level, children in the household, existing dogs, existing cats, experience level, and time available.

The endpoint is a full replacement operation rather than a partial update. The backend validates the complete profile before saving it.

The profile may also contain the adopter's preferred species, preferred sizes, and child age groups through the corresponding structured relationships.

## 6. Matching endpoint

### 6.1 Get potential matches

**GET** `/api/matches`

Returns animals that potentially match the authenticated adopter's current lifestyle profile.

The matching calculation is performed by the backend. The frontend does not calculate or modify match scores.

The matching service applies the deterministic rules defined by the matching requirements, including hard constraints and weighted soft factors where applicable.

The response may include:

- animal summary information
- a deterministic match score
- a match level such as `Potential match` or `Strong potential match`
- explanations describing the factors that contributed to the result

Matching is decision support only. A match result does not approve, reject, reserve, or guarantee an adoption.

Animals that do not match the adopter's current profile must not be treated as unavailable for ordinary browsing. The matching endpoint is a decision-support view rather than a replacement for animal discovery.

For identical relevant inputs, the matching service should produce identical results. Where scores are equal, results should be ordered by `animal_id` to provide deterministic ordering.

## 7. Favourite endpoints

### 7.1 List favourites

**GET** `/api/me/favourites`

Returns the authenticated adopter's saved animals.

### 7.2 Add favourite

**POST** `/api/me/favourites`

Adds an animal to the authenticated adopter's favourites.

The backend derives the adopter from the authenticated session. The client does not provide an adopter ID.

Adding the same animal more than once does not create duplicate favourite records. A duplicate request should return a conflict response according to the API error contract.

A favourite does not reserve an animal and does not affect animal availability.

### 7.3 Remove favourite

**DELETE** `/api/me/favourites/{animal_id}`

Removes the specified animal from the authenticated adopter's favourites.

## 8. Application endpoints

### 8.1 List my applications

**GET** `/api/applications`

Returns applications belonging to the authenticated adopter.

The backend derives the adopter from the authenticated session and does not accept an adopter ID as a client-controlled filter.

The response should provide enough information to track each application, including the animal, current status, and relevant submission information.

### 8.2 Get my application

**GET** `/api/applications/{application_id}`

Returns an application belonging to the authenticated adopter.

The backend verifies ownership before returning the application. An adopter must not be able to retrieve another adopter's application by changing the application ID.

The response includes the application's current status and status history.

Application profile information captured at submission time is treated as an immutable snapshot. Changes to the adopter's current lifestyle profile do not rewrite historical application data.

### 8.3 Submit application

**POST** `/api/applications`

Submits an adoption application for an animal.

The request contains only information that the adopter is expected to provide for the application:

- `animal_id`
- `reason_for_adoption`
- `care_plan`
- `additional_information`

The client does not provide the adopter ID, application status, submission timestamp, or other server-controlled values.

The submission workflow is handled by the application service and runs as a transaction.

The service performs the following checks before creating the application:

1. Authenticate the request.
2. Confirm that the authenticated user is an adopter.
3. Validate the submitted application fields.
4. Load the requested animal.
5. Confirm that the animal is currently `AVAILABLE`.
6. Confirm that the adopter does not already have an active application for the animal.
7. Confirm that the adopter does not have an application in `HOME_CHECK` or `APPROVED` for the same animal.
8. Load the adopter's current lifestyle profile.
9. Confirm that the profile is complete.
10. Begin the database transaction.
11. Create the application.
12. Copy the relevant current profile information into the application snapshot.
13. Create the initial `SUBMITTED` status-history record.
14. Commit the transaction.

The application snapshot is historical data. It must not change automatically when the adopter later edits their current profile.

Matching is not a prerequisite for submitting an application. An adopter may apply even when the matching system does not return a potential match.

The application service and database constraints must protect against duplicate active applications when concurrent requests attempt to submit the same application.

### 8.4 Withdraw application

**POST** `/api/applications/{application_id}/withdraw`

Requests withdrawal of an application belonging to the authenticated adopter.

The service verifies ownership and confirms that the current application state permits withdrawal before performing the state transition.

The transition is recorded in application status history.

## 9. Rescue application endpoints

### 9.1 List organisation applications

**GET** `/api/rescue/applications`

Returns applications for animals belonging to the authenticated rescue organisation.

The backend derives the organisation from the authenticated rescue staff session and scopes the query to that organisation.

Rescue staff must not be able to access applications belonging to another rescue organisation.

### 9.2 Get organisation application

**GET** `/api/rescue/applications/{application_id}`

Returns an application that belongs to the authenticated rescue organisation.

The service verifies that the application's animal belongs to a facility managed by the staff member's organisation before returning it.

### 9.3 Transition application status

**POST** `/api/rescue/applications/{application_id}/status`

Requests a transition from the application's current status to a specified new status.

The request contains the target status and an optional reason.

The backend validates the transition against the application state machine. The frontend cannot force an arbitrary status by sending a valid enum value.

Every successful status transition creates a status-history record containing the new status, timestamp, actor, and optional reason.

The actor is derived from the authenticated rescue staff session rather than supplied by the client.

Invalid state transitions are rejected.

### 9.4 Complete adoption

**POST** `/api/rescue/applications/{application_id}/complete-adoption`

Completes the adoption associated with an approved application.

This is a transactional workflow because it changes multiple related records.

The service verifies that the authenticated rescue staff user has authority over the application and animal before making the changes.

On successful completion:

- the selected application becomes `ADOPTED`
- the animal becomes `ADOPTED`
- other active applications for the same animal become `CLOSED_ANIMAL_ADOPTED`
- each resulting application state change is recorded in status history
- new applications for the adopted animal are blocked

The operation either commits all required changes or rolls them back if the transaction fails.

## 10. Organisation and facility endpoints

### 10.1 Get current organisation

**GET** `/api/rescue/organisation`

Returns the authenticated rescue staff member's organisation information.

The organisation is derived from the authenticated session.

### 10.2 Create facility

**POST** `/api/rescue/facilities`

Creates a facility belonging to the authenticated rescue organisation.

The backend assigns the organisation from the authenticated rescue staff session rather than accepting an arbitrary organisation ID from the client.

### 10.3 List organisation facilities

**GET** `/api/rescue/facilities`

Returns facilities belonging to the authenticated rescue organisation.

### 10.4 Update facility

**PATCH** `/api/rescue/facilities/{facility_id}`

Updates a facility belonging to the authenticated rescue organisation.

The service verifies organisation ownership before applying the update.

## 11. Rescue staff onboarding

Rescue staff accounts are created through controlled organisation invitations rather than public registration.

An invitation is associated with a specific organisation, recipient email address, role, and expiry time.

The invitation token is treated as a secret credential. The database stores a hash of the token rather than the raw token.

An invitation may be used only once and must not be usable after it expires.

The invitation determines the organisation and role of the account being created. The recipient chooses their password during account setup.

The client must not be able to change the organisation or role established by the invitation.

The exact invitation endpoint contract will be defined when the rescue onboarding workflow is implemented.

## 12. Authorisation and ownership

Authentication establishes who is making a request. Authorisation determines whether that authenticated user may perform the requested operation.

The API applies both role-based and organisation-based access control.

### 12.1 Adopter access

Adopters may:

- manage their own lifestyle profile
- browse publicly available animals
- view and manage their own favourites
- submit adoption applications
- view their own applications
- withdraw their own applications when permitted by the state machine
- view matching results generated from their current profile

Adopters must not access rescue management endpoints or another adopter's private data.

### 12.2 Rescue staff access

Rescue staff may manage animals, facilities, and applications belonging to their own organisation, subject to the relevant business rules.

Rescue staff must not access or modify records belonging to another rescue organisation.

The organisation boundary is derived from the authenticated user's server-side identity.

### 12.3 Ownership failures

For resources where revealing the existence of another organisation's or user's resource would itself disclose information, the API should use a not-found response rather than confirming that the resource exists.

Role failures should return a forbidden response when the authenticated user is known but lacks the required role.

The exact error response format is defined in the API error contract.

## 13. Validation and business rules

API validation occurs at multiple layers.

### 13.1 Request validation

Pydantic schemas validate request structure, data types, required fields, enum values, and basic input constraints at the API boundary.

### 13.2 Service validation

Services enforce business rules that cannot be expressed purely as request validation.

Examples include:

- whether an adopter profile is complete
- whether an animal is available for application
- whether an application already exists in a blocking state
- whether a status transition is valid
- whether a rescue staff member owns the relevant organisation or facility
- whether an adoption may be completed
- whether a rescue staff invitation is valid and unused

### 13.3 Database constraints

PostgreSQL enforces structural rules such as foreign keys, uniqueness, check constraints, and other integrity constraints.

Duplication and concurrency-sensitive business rules that require database enforcement should use appropriate database constraints in addition to service-level checks.

The API must not rely on frontend validation for security or business correctness.

## 14. API error handling

API errors should use a consistent JSON structure so that the frontend can distinguish validation, authentication, authorisation, conflict, not-found, and server errors.

The error contract should provide a stable machine-readable error code and a human-readable message.

At minimum, the API should distinguish:

- `400` for malformed or otherwise invalid requests where appropriate
- `401` for unauthenticated requests
- `403` for authenticated users without the required role or permission
- `404` when a requested resource is not available to the caller
- `409` for conflicts such as duplicate favourites or application submission conflicts
- `422` for request validation failures handled by Pydantic
- `500` for unexpected server errors

Authentication failures should not reveal whether a particular account exists.

Unexpected internal errors should not expose stack traces, database details, credentials, or other implementation-sensitive information to the client.

## 15. Pagination and filtering

Collection endpoints should support pagination where the result set can grow beyond a practical single response.

Animal discovery should support query parameters for the filters defined by the product requirements.

Pagination responses should provide enough information for the frontend to determine the current result set and whether additional results are available.

Filtering and pagination are applied by the backend. The frontend must not retrieve an unrestricted dataset and perform authoritative filtering locally.

Where an endpoint has a defined deterministic ordering, that ordering should remain stable across requests unless the underlying data changes.

## 16. Application state machine

Application status changes are controlled by an explicit state machine.

The valid transitions are:

| Current status | Allowed next statuses |
| --- | --- |
| `SUBMITTED` | `UNDER_REVIEW`, `WITHDRAWN`, `DECLINED`, `CLOSED_ANIMAL_ADOPTED` |
| `UNDER_REVIEW` | `HOME_CHECK`, `WITHDRAWN`, `DECLINED`, `CLOSED_ANIMAL_ADOPTED` |
| `HOME_CHECK` | `APPROVED`, `WITHDRAWN`, `DECLINED`, `CLOSED_ANIMAL_ADOPTED` |
| `APPROVED` | `ADOPTED`, `WITHDRAWN` |
| `ADOPTED` | none |
| `DECLINED` | none |
| `WITHDRAWN` | none |
| `CLOSED_ANIMAL_ADOPTED` | none |

The backend service is responsible for enforcing this state machine.

The client may request a target status, but it cannot choose an otherwise invalid transition.

Every successful transition creates a status-history record. The history records the resulting status, when the change occurred, which authenticated user made the change, and an optional reason.

Application status history is append-only from the API's perspective. Existing history entries must not be rewritten to represent later state changes.

## 17. Security considerations

Authentication uses server-managed sessions and secure HTTP-only browser cookies as described in `architecture.md`.

The session identifier must not be exposed through normal client-side application storage such as local storage.

Authenticated endpoints must establish the current user from the server-side session.

CSRF protection is required for state-changing requests because authentication relies on a browser cookie. The exact CSRF mechanism will be selected during authentication implementation.

Role checks and organisation ownership checks must be performed on the backend.

Client-provided organisation IDs, adopter IDs, user IDs, roles, application statuses, timestamps, and similar server-controlled values must not be trusted to establish authority.

Password storage must use a secure password-hashing algorithm. Plain-text passwords must never be stored or returned through the API.

Invitation tokens must be stored as hashes and must expire after their configured lifetime or after successful use.

API responses must not expose credentials, password hashes, session secrets, raw invitation tokens, or unnecessary internal database information.

Public endpoints should expose only information intended for public animal discovery. Private adopter and rescue information must remain behind the appropriate authentication and authorisation boundaries.

Security controls are enforced by the backend rather than relying on the React client to enforce them.

## 18. Implementation status

The API design is currently ahead of the implementation.

### Implemented

- FastAPI application
- `/api/health` endpoint
- PostgreSQL connection configuration
- SQLAlchemy database engine
- SQLAlchemy domain models
- Initial PostgreSQL schema and Alembic migration

### Designed but not implemented

- adopter registration
- login and logout
- server-side sessions
- authentication middleware/dependencies
- CSRF protection
- authenticated user endpoint
- public animal endpoints
- rescue animal management endpoints
- adopter profile endpoints
- matching endpoint and matching service
- favourite endpoints
- adopter application endpoints
- rescue application endpoints
- organisation and facility endpoints
- invitation workflow endpoints
- Pydantic request and response schemas
- repository implementations
- service-layer business logic
- consistent API error response handling
- pagination and collection response contracts

### Implementation alignment still required

The current database schema does not yet contain every structure required by the API design.

In particular:

- application scalar snapshot fields still need to be implemented
- application snapshot data must be persisted immutably at submission time
- status-history actor information still needs to be implemented
- the database needs the active-application uniqueness rule required to protect concurrent submissions

These are implementation gaps rather than reasons to weaken the API contract.

## 19. Deferred API concerns

The following concerns are intentionally deferred unless the product requirements justify them:

- API versioning
- rate limiting
- response caching
- WebSockets
- background job processing
- GraphQL
- a separate public API

These concerns can be introduced later without changing the core separation between API routes, services, repositories, and the database.

## 20. Related documentation

- `docs/product/requirements.md` — product and acceptance requirements
- `docs/product/product-overview.md` — product purpose, users, scope, and boundaries
- `docs/architecture/architecture.md` — system architecture and responsibility boundaries
- `docs/architecture/technology-decisions.md` — technology choices and engineering reasoning
- `docs/data/data-model.md` — database and domain data model
- `docs/engineering/security.md` — detailed security engineering decisions and controls
