# Requirements

## 1. Purpose

This document defines the functional and non-functional requirements for the Raise 'n Rescue MVP.

The requirements describe what the system must do and the rules it must enforce. They are intentionally separated from implementation details such as the specific Python classes, database tables or React components used to implement them.

The MVP focuses on dogs and cats and covers the adoption journey from animal discovery through application tracking and adoption completion.

## 2. Actors

### 2.1 Prospective adopter

A prospective adopter can:

- create and manage an adopter account;
- maintain a lifestyle profile;
- browse available animals;
- filter animals;
- view animal profiles;
- view potential matches;
- understand the factors contributing to a match;
- favourite animals;
- submit adoption applications;
- view their own applications;
- withdraw eligible applications;
- view application status history.

### 2.2 Rescue staff

Rescue staff operate within a specific rescue organisation.

They can:

- manage animals belonging to their organisation;
- maintain animal compatibility information;
- view applications for their organisation's animals;
- update application statuses according to the allowed workflow;
- manage organisation facilities;
- complete adoption workflows.

Rescue staff must not access operational data belonging to another organisation.

### 2.3 System

The system is responsible for:

- enforcing authentication and authorisation;
- validating input;
- enforcing business rules;
- calculating deterministic matching results;
- maintaining application state transitions;
- maintaining status history;
- maintaining data consistency during multi-record workflows;
- enforcing structural database constraints.

## 3. Authentication and authorisation

### AUTH-01 - Adopter registration

The system must allow a new adopter to register using an email address and password.

Public registration creates an adopter account only.

A public user must not be able to create a rescue staff account by selecting a rescue role.

### AUTH-02 - Authentication

The system must authenticate users using their registered credentials.

Invalid authentication attempts must return a generic authentication error rather than revealing whether an email address exists.

### AUTH-03 - Session management

Authenticated sessions must be managed by the backend.

The session mechanism must use secure HTTP-only cookies and must not require the frontend to store authentication tokens in local storage.

State-changing requests must include appropriate CSRF protection for the chosen session implementation.

### AUTH-04 - Current user

An authenticated user must be able to retrieve their current account and role information.

The backend must derive the authenticated user's identity from the server-managed session rather than accepting an adopter or staff user ID from the client as an authority value.

### AUTH-05 - Logout

An authenticated user must be able to terminate their session.

### AUTH-06 - Role authorisation

The system must enforce role-based access.

Adopter-only operations must not be accessible to rescue staff unless explicitly designed otherwise.

Rescue operations must require the rescue staff role.

### AUTH-07 - Organisation authorisation

Every rescue staff account belongs to one rescue organisation.

The backend must derive the organisation boundary from the authenticated staff account.

A rescue staff member must not be able to access, modify or manage data belonging to another organisation by supplying another organisation's ID.

### AUTH-08 - Controlled rescue onboarding

Rescue staff accounts must be created through controlled organisation onboarding.

The MVP uses organisation invitations rather than unrestricted public rescue registration.

An invitation identifies the organisation and role and must be time-limited and usable only once.

## 4. Animal management

### ANIMAL-01 - Animal creation

Authorised rescue staff must be able to create animals belonging to their organisation.

An animal must be associated with a facility belonging to the same organisation.

### ANIMAL-02 - Animal information

An animal must support structured information including:

- name;
- species;
- age value;
- age unit;
- date on which the recorded age was established;
- sex;
- size;
- facility;
- energy level;
- personality description;
- personality traits;
- compatibility with children;
- compatibility with dogs;
- compatibility with cats;
- suitable home type;
- outdoor-space requirement;
- experience requirement;
- description;
- availability status;
- timestamps.

The MVP supports dogs and cats only.

### ANIMAL-03 - Animal age

Animal age values must be zero or greater.

The recorded age date must be updated when the underlying age information changes.

### ANIMAL-04 - Animal photos

An animal may have multiple photos.

An animal may have at most one primary photo.

Photo display order must be represented explicitly.

### ANIMAL-05 - Animal status

Animals must have a controlled status.

The MVP statuses are:

- `AVAILABLE`
- `ADOPTION_PENDING`
- `ADOPTED`
- `UNAVAILABLE`

### ANIMAL-06 - Animal discovery visibility

Available animals must be included in adopter discovery.

Animals that are adoption pending or adopted must not appear as available discovery results.

A direct animal profile may still expose appropriate information about an animal that is no longer available.

### ANIMAL-07 - Animal updates

Authorised rescue staff may update animals belonging to their organisation.

Animal ownership must be checked by the backend.

### ANIMAL-08 - Compatibility data

Rescue staff are responsible for maintaining the structured compatibility information used by the matching system.

The matching system must use the current stored animal information.

## 5. Animal discovery

### DISC-01 - Animal listing

Prospective adopters must be able to retrieve a list of available animals.

### DISC-02 - Filtering

The animal listing must support relevant structured filters, including where applicable:

- species;
- sex;
- size;
- age;
- energy level;
- compatibility characteristics;
- suitable home type;
- outdoor-space requirement;
- experience requirement;
- facility or textual location information.

The MVP does not provide radius or distance-based geospatial filtering.

### DISC-03 - Animal detail

Prospective adopters must be able to retrieve a detailed animal profile.

The detail response may include more information than the discovery summary.

### DISC-04 - Browse outside matches

Matching must not restrict ordinary animal browsing.

An adopter must still be able to discover and view animals that are not returned as potential matches.

## 6. Adopter profile

### PROFILE-01 - Adopter lifestyle profile

An adopter must be able to create and maintain a structured lifestyle profile.

The profile includes:

- home type;
- outdoor space;
- activity level;
- children in household;
- existing dogs;
- existing cats;
- experience level;
- time available.

### PROFILE-02 - Preferred characteristics

The adopter profile must support preferred:

- species;
- sizes;
- child age groups.

These are preferences used as matching inputs and are not guarantees about what an adopter will accept.

### PROFILE-03 - Profile ownership

An adopter may only view and modify their own profile.

The backend must derive the adopter profile from the authenticated user.

### PROFILE-04 - Profile completeness

The system must validate required lifestyle information before using the profile for matching or submitting an application where the workflow requires a complete profile.

## 7. Matching

### MATCH-01 - Structured matching inputs

Matching must use structured animal and adopter attributes rather than relying only on free-text descriptions.

### MATCH-02 - Deterministic results

The matching algorithm must be deterministic.

The same animal and adopter inputs must produce the same result.

### MATCH-03 - Hard constraints

The matching system must be able to identify hard incompatibilities.

A hard incompatibility must prevent an animal from being classified as a potential match.

### MATCH-04 - Soft preferences

Soft compatibility factors may contribute positively or negatively to a matching score without automatically determining the adoption outcome.

### MATCH-05 - Unknown values

Unknown animal compatibility information must not automatically be treated as compatible.

The system must handle unknown values explicitly according to the matching rules.

### MATCH-06 - Compatibility dimensions

The matching system must consider relevant dimensions including where applicable:

- home type;
- outdoor space;
- activity or energy level;
- animal size;
- existing dogs;
- existing cats;
- children;
- animal compatibility with children;
- adopter experience;
- time available;
- preferred species;
- preferred size;
- preferred child age group.

### MATCH-07 - Explainability

A matching result must include enough information for the frontend to explain the relevant factors contributing to the result.

### MATCH-08 - Match levels

The MVP must classify sufficiently compatible animals using defined scoring thresholds:

- `Potential match`
- `Strong potential match`

### MATCH-09 - No decision authority

Matching must never:

- approve an application;
- reject an application;
- reserve an animal;
- make the final adoption decision.

### MATCH-10 - No browsing gate

A user must not be prevented from viewing or applying for an animal because the matching system did not classify it as a potential match.

### MATCH-11 - No-match fallback

If no animals meet the matching criteria, the system must provide a useful empty state rather than implying that no animal could ever be suitable.

### MATCH-12 - Current profile

Matching must use the adopter's current profile information.

Matching results are guidance and do not become a permanent record of an adoption decision.

### MATCH-13 - Ordering

When multiple matching results have the same score, results must use a deterministic secondary ordering based on the animal ID.

### MATCH-14 - Future machine learning

Machine-learning matching is outside the MVP.

It must not be introduced as a replacement for the deterministic matching system until there is enough real structured data and adoption outcome data to evaluate it properly.

## 8. Favourites

### FAV-01 - Add favourite

An authenticated adopter must be able to favourite an animal.

### FAV-02 - Remove favourite

An authenticated adopter must be able to remove one of their favourites.

### FAV-03 - View favourites

An adopter must be able to retrieve their own favourites.

### FAV-04 - Duplicate favourite

The same adopter must not be able to create duplicate favourite records for the same animal.

### FAV-05 - No reservation

A favourite must never reserve an animal or change the animal's availability status.

## 9. Adoption applications

### APP-01 - Application submission

An authenticated adopter must be able to submit an application for an available animal.

The application must include:

- animal ID;
- reason for adoption;
- care plan;
- additional information.

### APP-02 - Matching is not required

An adopter does not need to receive a potential match before applying.

A matching result must not be used as an application eligibility gate.

### APP-03 - Applicant identity

The backend must derive the applicant from the authenticated session.

The client must not be allowed to submit an arbitrary adopter ID.

### APP-04 - Application status

A newly submitted application must start in:

`SUBMITTED`

The client must not be able to choose the initial status.

### APP-05 - Submission validation

Before creating an application, the backend must validate:

- the adopter is authenticated;
- the adopter profile exists;
- the animal exists;
- the animal is available;
- the application data is valid;
- the adopter is not blocked by an existing active application for the same animal;
- the adopter's lifestyle profile is complete.

### APP-06 - Active application uniqueness

An adopter must not have more than one active application for the same animal.

The database must enforce the structural uniqueness rule required to protect against concurrent duplicate submissions.

### APP-07 - Application snapshots

Matching uses the adopter's current lifestyle profile, while the application preserves a snapshot of the relevant profile information at submission time.

The application snapshot must remain unchanged if the adopter later changes their current profile.

The snapshot includes the relevant scalar lifestyle values and the preferred species, sizes and child age groups applicable to the application.

### APP-08 - Application immutability

Application submission information and profile snapshots must not be silently rewritten when the adopter changes their current profile.

### APP-09 - Application retrieval

An adopter may retrieve only their own applications.

An adopter must be able to see the current status and relevant application information.

### APP-10 - Application history

An adopter must be able to view the status history of their own applications.

### APP-11 - Application withdrawal

An adopter may withdraw an application only when the current application status allows withdrawal.

The backend must enforce the allowed transitions.

### APP-12 - Rescue application access

Rescue staff may retrieve applications for animals belonging to their organisation.

They must not retrieve applications belonging to another organisation.

## 10. Application status workflow

Applications must follow a controlled state machine.

### Allowed transitions

`SUBMITTED` may transition to:

- `UNDER_REVIEW`
- `WITHDRAWN`
- `DECLINED`
- `CLOSED_ANIMAL_ADOPTED`

`UNDER_REVIEW` may transition to:

- `HOME_CHECK`
- `WITHDRAWN`
- `DECLINED`
- `CLOSED_ANIMAL_ADOPTED`

`HOME_CHECK` may transition to:

- `APPROVED`
- `WITHDRAWN`
- `DECLINED`
- `CLOSED_ANIMAL_ADOPTED`

`APPROVED` may transition to:

- `ADOPTED`
- `WITHDRAWN`

The following statuses are terminal:

- `ADOPTED`
- `DECLINED`
- `WITHDRAWN`
- `CLOSED_ANIMAL_ADOPTED`

### APP-13 - Invalid transitions

The backend must reject application status transitions that are not defined by the state machine.

### APP-14 - Transition actor

Every application status transition must record the actor responsible for the change.

### APP-15 - Transition timestamp

Every application status transition must record when the change occurred.

### APP-16 - Transition reason

A rescue-side status transition may include a reason or note.

The reason is nullable where the workflow does not require one.

### APP-17 - History integrity

A successful status transition must create the corresponding status history record as part of the same transaction.

## 11. Adoption completion

### ADOPT-01 - Complete adoption

Adoption completion must be handled as a transaction because it changes multiple related records.

### ADOPT-02 - Successful application

The approved application being completed must transition to:

`ADOPTED`

### ADOPT-03 - Animal status

The adopted animal must transition to:

`ADOPTED`

### ADOPT-04 - Other active applications

Other active applications for the same animal must transition to:

`CLOSED_ANIMAL_ADOPTED`

### ADOPT-05 - History

Every application transition caused by adoption completion must have corresponding status history.

### ADOPT-06 - Consistency

The adoption workflow must not leave the database in a state where an animal is adopted but the successful application or other active applications have not been updated.

## 12. Rescue organisation and facilities

### ORG-01 - Organisation

The system must support rescue organisations as operational ownership boundaries.

### ORG-02 - Facilities

An organisation may have multiple facilities.

Each facility belongs to exactly one organisation.

### ORG-03 - Animal ownership

Each animal belongs to a facility, and the facility must belong to the same organisation as the rescue staff managing it.

### ORG-04 - Staff ownership

Each rescue staff user belongs to exactly one organisation.

### ORG-05 - Tenant isolation

Rescue staff queries and mutations must be organisation-scoped.

The backend must not trust organisation identifiers supplied by the client to establish ownership.

## 13. Business rules

The following rules apply across the system:

1. Public registration creates adopter accounts only.
2. Rescue staff accounts require controlled organisation onboarding.
3. Adopters can access only their own private profile, favourites and applications.
4. Rescue staff can access only data belonging to their organisation.
5. Animal ownership is determined through the organisation and facility relationship.
6. Matching is advisory and never makes an adoption decision.
7. Matching does not reserve animals.
8. Favourites do not reserve animals.
9. Matching is not required to submit an application.
10. Applications may only be submitted for animals that are available at the time of submission.
11. An adopter may not have multiple active applications for the same animal.
12. Application state changes must follow the defined state machine.
13. Terminal application states cannot transition to another state.
14. Status history must be recorded when application status changes.
15. Adoption completion must update all affected application and animal records consistently.
16. Application snapshots preserve the relevant adopter information from the time of submission.
17. Current adopter profile changes must not rewrite historical application snapshots.
18. Unknown animal compatibility information must not automatically count as compatible.
19. Users must not be able to bypass backend business rules by manipulating frontend requests.
20. Important structural data integrity rules must also be enforced by the database where practical.

## 14. Non-functional requirements

### NFR-01 - Security

Security-sensitive operations must be enforced by the backend.

The frontend must not be treated as a security boundary.

### NFR-02 - Authorisation

Authorisation must be checked for every protected resource and operation.

### NFR-03 - Tenant isolation

Rescue organisation boundaries must be enforced server-side.

### NFR-04 - Data integrity

The database must enforce important structural constraints such as:

- primary keys;
- foreign keys;
- uniqueness;
- required values;
- valid enum values;
- valid non-negative numeric values where appropriate.

### NFR-05 - Transactional consistency

Workflows that update multiple related records must use transactions.

### NFR-06 - Determinism

Matching and other rule-based business logic must behave deterministically for the same inputs.

### NFR-07 - Testability

Business logic must be structured so that it can be tested independently of the HTTP layer where practical.

### NFR-08 - Maintainability

The backend must use clear separation between:

- API routes;
- services/business logic;
- repositories/data access;
- database models.

### NFR-09 - Validation

Input must be validated at appropriate boundaries.

Client-side validation may improve user experience but must not replace backend validation.

### NFR-10 - Accessibility

The frontend should provide accessible forms, navigation, status information and interactive controls.

### NFR-11 - Responsive design

The application should remain usable across common desktop and mobile viewport sizes.

### NFR-12 - Error handling

The API must return predictable error responses that allow the frontend to display useful validation, authorisation and workflow errors without exposing sensitive implementation details.

### NFR-13 - Observability

Important application failures and security-relevant events should be logged in a way that supports debugging without unnecessarily logging sensitive user information.

## 15. Public and private boundaries

The public-facing product may expose:

- available animal discovery information;
- appropriate animal profile information;
- authentication endpoints required for registration and login.

Private adopter information must not be exposed through public animal or application endpoints.

Private application information must be visible only to the relevant adopter and authorised rescue staff for the owning organisation.

Rescue operational data must not be exposed across organisation boundaries.

## 16. MVP exclusions

The following are explicitly outside the MVP:

- machine-learning matching;
- AI-generated animal descriptions;
- chatbot functionality;
- lost-pet functionality;
- donations and payments;
- messaging and notifications;
- maps;
- distance-based or radius search;
- social features and reviews;
- advanced recommendation systems;
- additional animal species;
- complex administration and analytics;
- native mobile applications;
- microservices;
- Kubernetes;
- public rescue organisation registration;
- automatic adoption approval or rejection.

## 17. Acceptance criteria

The following acceptance criteria are the canonical MVP acceptance criteria.

### AC-01 - Registration

A user can register as an adopter using valid credentials, and public registration cannot create a rescue staff account.

### AC-02 - Authentication

A registered user can log in, maintain an authenticated session and log out.

Invalid credentials do not reveal whether an account exists.

### AC-03 - Role authorisation

Protected operations reject users who do not have the required role.

### AC-04 - Organisation isolation

Rescue staff can access and modify only data belonging to their organisation.

### AC-05 - Animal discovery

An adopter can retrieve available dogs and cats and filter the results using supported structured attributes.

### AC-06 - Animal profile

An adopter can open an animal profile and view the information required to understand its characteristics, needs and compatibility.

### AC-07 - Adopter profile

An adopter can create and update their lifestyle profile and preferred characteristics.

### AC-08 - Matching

Given the same adopter profile and animal data, the matching system produces the same result.

### AC-09 - Matching explanation

A matching result includes information that allows the relevant compatibility factors to be explained.

### AC-10 - Matching boundaries

Matching does not approve, reject or reserve animals and does not prevent ordinary browsing or application submission.

### AC-11 - Favourites

An adopter can add and remove favourites, and duplicate favourites are prevented.

### AC-12 - Application submission

An adopter can submit an application for an available animal with the required application information.

### AC-13 - Application identity

The backend derives the applicant from the authenticated session rather than trusting an adopter ID supplied by the client.

### AC-14 - Application uniqueness

An adopter cannot have more than one active application for the same animal.

### AC-15 - Application snapshot

Submitting an application preserves the relevant adopter profile information from that point in time.

Changing the current adopter profile later does not alter the stored application snapshot.

### AC-16 - Application state machine

Application status changes are limited to the defined valid transitions.

Invalid transitions are rejected.

### AC-17 - Application history

Every successful application status transition creates a corresponding history record containing the new status, actor and timestamp, with an optional reason where applicable.

### AC-18 - Application visibility

Adopters can view only their own applications.

Rescue staff can view applications only for animals belonging to their organisation.

### AC-19 - Adoption completion

Completing an adoption updates the successful application, animal and other active applications consistently within one transaction.

### AC-20 - Data integrity

Database constraints prevent structurally invalid relationships and required uniqueness violations.

### AC-21 - Security boundary

Business rules and authorisation cannot be bypassed by manipulating frontend requests or directly supplying identifiers belonging to another user or organisation.

## 18. Implementation status

The requirements describe the intended MVP behaviour.

The current codebase contains the initial project foundation, SQLAlchemy models and database migration, but the complete application behaviour is not implemented yet.

In particular, the following requirements are designed but not yet fully implemented:

- complete authentication and session management;
- organisation invitation onboarding;
- full animal management API;
- adopter profile API;
- deterministic matching service;
- favourites API;
- application submission workflow;
- application snapshots;
- application state transition service;
- adoption completion workflow;
- complete authorisation enforcement;
- automated test coverage.

The implementation should be brought into alignment with these requirements rather than changing the requirements simply to match incomplete code.

## 19. Deferred product direction

Future features may extend the product with machine learning, additional species, geospatial discovery, messaging, notifications, analytics and other capabilities.

These are intentionally deferred so that the MVP can establish a reliable core adoption workflow first.
