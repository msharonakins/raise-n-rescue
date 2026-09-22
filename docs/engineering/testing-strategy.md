# Testing strategy

This document defines how Raise 'n Rescue will be tested across the backend, database, API, frontend, and complete user workflows.

The strategy focuses on verifying behaviour and business rules rather than treating test coverage as the only measure of quality.

The current project foundation does not yet contain the full automated test suite described here. The testing strategy therefore documents the intended testing approach and identifies the areas that must be covered as implementation progresses.

## 1. Testing principles

Testing should:

- verify observable behaviour and business rules
- catch regressions when existing functionality changes
- test important failure paths as well as successful paths
- keep deterministic business logic independently testable
- verify security and authorisation boundaries
- test database constraints where they protect important invariants
- use realistic integration tests for workflows that depend on PostgreSQL
- keep tests understandable and maintainable
- avoid relying on a single type of test for confidence

Test coverage is a useful signal, but a high coverage percentage does not by itself demonstrate that the system is correct.

## 2. Testing layers

Testing is organised into several complementary layers:

### Unit tests

Unit tests verify small pieces of application logic in isolation.

They are particularly important for:

- matching rules
- hard compatibility constraints
- match scoring
- match-level classification
- explanation generation
- application state-transition rules
- profile completeness rules
- adoption workflow rules
- other deterministic service and domain logic

Unit tests should be fast and should not require a running database unless the behaviour being tested specifically belongs to the database boundary.

### Integration tests

Integration tests verify interactions between application components and PostgreSQL.

They should cover:

- repository queries
- foreign-key relationships
- database constraints
- transaction behaviour
- application snapshot persistence
- application status history
- active-application uniqueness
- organisation-scoped data access

These tests should use PostgreSQL rather than replacing important database behaviour with an in-memory substitute.

### API tests

API tests verify the behaviour exposed through FastAPI routes.

They should cover:

- request validation
- authentication
- role-based authorisation
- organisation isolation
- successful responses
- expected error responses
- application submission
- application withdrawal
- status transitions
- adoption completion
- animal discovery and filtering
- favourites
- adopter profile management

API tests should verify the complete request-to-service-to-database behaviour where appropriate rather than testing route functions in isolation only.

## 3. Frontend testing

Frontend tests should verify user-facing behaviour and component interactions.

They should cover:

- rendering of important UI states
- form validation and submission
- loading states
- error states
- authentication-related UI behaviour
- animal discovery and filtering
- animal profile presentation
- adopter profile editing
- match result presentation and explanations
- favourites
- application submission
- application status and history presentation
- rescue staff workflows

Frontend tests should not duplicate backend business-rule tests. The backend remains authoritative for validation, authorisation, matching, and workflow rules.

## 4. End-to-end testing

End-to-end tests should cover a small number of critical user journeys through the running application.

The highest-value journeys include:

1. An adopter registers, completes their profile, discovers animals, and views potential matches.
2. An adopter favourites an animal and later removes the favourite.
3. An adopter submits an application and views its status history.
4. Rescue staff review an application and move it through valid workflow states.
5. Rescue staff complete an adoption and the system updates the adopted animal and related applications consistently.

End-to-end coverage should remain focused on critical workflows rather than attempting to reproduce every unit or API test through the browser.

## 5. Matching tests

Matching is deterministic and therefore requires strong automated coverage.

Tests should verify:

- identical inputs produce identical results
- hard compatibility failures exclude an animal from potential matching
- unknown animal information is not automatically treated as compatible
- soft factors contribute according to the defined scoring rules
- match levels are assigned consistently
- explanations correspond to the factors that affected the result
- animals outside the match results remain discoverable through normal browsing
- matching never approves, rejects, reserves, or otherwise makes an adoption decision
- incomplete adopter profiles are handled according to the defined product rules

Matching tests should include positive cases, negative cases, unknown-data cases, boundary cases, and combinations of multiple factors.

## 6. Application workflow tests

Application workflows should be tested against the defined state machine.

Tests should verify:

- only valid status transitions are accepted
- invalid transitions are rejected
- terminal states cannot be changed through normal status transitions
- withdrawal is available only where the workflow permits it
- application history records each successful transition
- the actor responsible for a status change is recorded when the audit field is implemented
- adopters can access only their own applications
- rescue staff can access only applications belonging to their organisation
- matching is not required before an adopter can apply

Application submission should also verify that:

- the animal is eligible for a new application
- duplicate active applications are prevented
- the adopter's current profile is captured as an immutable snapshot
- later profile changes do not alter existing application snapshots
- the application and initial status-history record are persisted together

## 7. Adoption completion tests

Adoption completion is a multi-record transaction and requires integration testing.

Tests should verify that a successful adoption completion:

- changes the selected application to `ADOPTED`
- changes the animal to `ADOPTED`
- changes other active applications for the same animal to `CLOSED_ANIMAL_ADOPTED`
- records the relevant status-history entries
- prevents new applications for the adopted animal
- leaves the database in a consistent state if an operation fails

The transaction should be tested for both successful completion and rollback behaviour.

## 8. Database integrity tests

Database tests should verify constraints that protect important domain invariants.

These include:

- unique user email addresses
- unique personality trait names
- one adopter profile per user
- valid foreign-key relationships
- non-negative animal ages
- non-negative animal photo display orders
- at most one primary photo per animal
- valid enum values
- adopter preference relationship uniqueness
- application preference snapshot relationship uniqueness
- role and organisation consistency for users
- prevention of multiple active applications for the same adopter and animal when the required database constraint is implemented

Database integrity tests should verify both valid data and rejected invalid data where the constraint is important to the application.

## 9. Security and authorisation testing

Security-sensitive behaviour should have automated regression tests where practical.

Tests should verify:

- unauthenticated users cannot access protected endpoints
- adopters cannot perform rescue-staff operations
- rescue staff cannot access another organisation's records
- adopters cannot access another adopter's applications or profile data
- users cannot modify protected ownership or workflow fields through API input
- invalid or expired organisation invitations are rejected
- used invitations cannot be reused
- logout invalidates the authenticated session
- invalid credentials produce the expected generic authentication failure

Security tests should focus on server-side enforcement because the React client is not a security boundary.

## 10. Test data and fixtures

Tests should use controlled test data that represents realistic domain scenarios without depending on production data.

Fixtures should make it straightforward to create:

- adopter users and profiles
- rescue organisations and rescue staff
- facilities
- animals with different compatibility attributes
- favourites
- applications in different workflow states
- application history records
- organisation invitations

Matching fixtures should make individual factors explicit so that a failing test can be understood from the input data.

Integration tests should isolate their database state so that one test does not depend on data created by another test.

## 11. Regression testing

Whenever a defect is discovered, a regression test should be added when practical before or alongside the fix.

This is particularly important for:

- matching edge cases
- application state transitions
- organisation isolation
- application snapshot immutability
- concurrent application submission
- adoption completion
- authentication and authorisation

The purpose is to prevent a previously fixed defect from silently returning as the codebase changes.

## 12. Implementation status

The project now has a basic automated testing foundation using pytest.

The current foundation includes:

- pytest installed as a development dependency
- explicit pytest configuration through `pytest.ini`
- a `tests/` test suite directory
- a `tests/unit/` unit-test directory
- an initial unit test covering selected domain enum values
- successful pytest discovery and execution of the current tests

The broader automated testing structure and feature-level test suite described in this document are not yet implemented.

Testing requirements that depend on currently incomplete application functionality will be implemented alongside those features rather than being treated as completed documentation-only requirements.

In particular, tests will need to be added as the following areas are implemented:

- backend domain and service logic
- PostgreSQL integration and database integrity
- authentication and server-managed sessions
- role-based authorisation and organisation isolation
- adopter profile workflows
- animal discovery and filtering
- deterministic matching
- favourites
- application submission and snapshots
- application status transitions
- adoption completion
- rescue organisation workflows
- frontend behaviour
- critical end-to-end user journeys

## 13. Definition of testing completeness

A feature should not be considered complete simply because its implementation runs successfully.

For a meaningful feature, completion should include the relevant automated tests, successful validation of important failure paths, and verification that existing functionality has not regressed.

The level of testing should be appropriate to the risk and complexity of the feature, with particular attention to business rules, security boundaries, data integrity, and multi-record workflows.
