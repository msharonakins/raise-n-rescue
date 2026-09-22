# Data model

This document defines the data model for Raise 'n Rescue, including the main domain entities, relationships, constraints, and data ownership boundaries.

The data model supports the product requirements and the backend architecture. PostgreSQL is responsible for structural data integrity, while application services enforce business rules that require application-level logic.

The current database implementation should be read together with this design. Where a required structure has been designed but is not yet implemented, that gap is identified explicitly rather than being treated as completed.

## 1. Data model principles

- Model the core adoption workflow directly in the database rather than storing important domain state only as unstructured data.
- Use foreign keys to enforce relationships between related entities.
- Use database constraints for structural rules such as uniqueness, valid ranges, and required relationships.
- Keep authentication identity separate from adopter lifestyle information.
- Keep rescue organisation ownership explicit so rescue-side data can be scoped securely.
- Store application history independently from the adopter's current profile.
- Preserve application snapshots as historical data that does not change when the current adopter profile changes.
- Keep application status history append-only from the API perspective.
- Use deterministic, structured data for the matching inputs rather than relying only on free-text descriptions.
- Do not introduce geospatial infrastructure into the MVP. Location is represented through facilities and textual location information.

## 2. Data ownership boundaries

The main ownership boundaries are:

| Data area | Primary owner | Purpose |
| --- | --- | --- |
| User account | User/authentication system | Identity, credentials, role, and account status |
| Adopter profile | Adopter | Current lifestyle information used for matching |
| Rescue organisation | Rescue organisation | Organisation identity and contact information |
| Facility | Rescue organisation | Physical or operational location associated with animals |
| Animal | Rescue organisation | Animal profile, compatibility information, and adoption status |
| Favourite | Adopter | Saved animal relationship |
| Application | Adopter and rescue organisation | Adoption application and its current workflow state |
| Application snapshot | Application | Historical adopter information captured at submission |
| Application status history | Application workflow | Audit trail of application state changes |

## 3. Entity relationship overview

The main relationships are:

- A rescue organisation has many facilities.
- A facility belongs to one rescue organisation and can contain many animals.
- An animal belongs to one facility.
- An animal can have many photos.
- An animal can have many personality traits, and a personality trait can describe many animals.
- A user represents an authenticated account.
- An adopter user has one adopter profile.
- An adopter profile can have multiple preferred species, preferred sizes, and child age groups.
- An adopter profile can have many favourites.
- An animal can be favourited by many adopters.
- An adopter profile can have many applications.
- An animal can have many applications over its adoption lifecycle.
- An application has status-history records describing its workflow changes.
- Rescue staff users belong to one rescue organisation.
- Rescue organisations can have many controlled onboarding invitations.

The database therefore connects the product journey from discovery through application tracking and adoption completion.

## 4. User and authentication model

The `users` table represents authenticated accounts for both adopters and rescue staff.

Each user has:

- a UUID primary key
- a unique email address
- a password hash
- a role
- an account status
- an optional rescue organisation relationship
- creation and update timestamps

The user role determines the broad type of account:

- `ADOPTER` - a public adopter account
- `RESCUE_STAFF` - a staff account belonging to a rescue organisation

The database applies a role and organisation consistency rule:

- an adopter must not belong to a rescue organisation
- rescue staff must belong to a rescue organisation

The organisation relationship is therefore nullable at the database level but constrained according to the user role.

Authentication credentials belong to the user account. Adopter lifestyle information is stored separately in `adopter_profiles`.

Server-managed sessions are part of the authentication architecture but are not yet represented by a `sessions` table in the current implementation. The session data model will be added when authentication is implemented.

## 5. Rescue organisation model

The `rescue_organisations` table represents a rescue organisation using the platform.

Each organisation has:

- a UUID primary key
- organisation name
- contact email
- contact phone
- address
- creation and update timestamps

An organisation can have:

- many rescue staff users
- many facilities
- many organisation invitations

Organisation ownership is an important security boundary. Rescue staff operations must be restricted to records belonging to the authenticated staff member's organisation.

## 6. Facility model

The `facilities` table represents a facility belonging to a rescue organisation.

Each facility has:

- a UUID primary key
- an organisation foreign key
- facility name
- address
- contact phone
- creation and update timestamps

A facility belongs to exactly one rescue organisation.

A facility can contain many animals. The animal's facility relationship provides the organisation ownership path used by rescue-side authorisation.

Facilities also provide the MVP's location context for animals. The data model does not include latitude, longitude, radius, PostGIS geometry, or other geospatial fields.

## 7. Organisation invitation model

The `organisation_invitations` table supports controlled onboarding of rescue staff.

Each invitation contains:

- a UUID primary key
- the target organisation
- the recipient email address
- the role to be assigned
- a hashed invitation token
- an expiry timestamp
- an optional used timestamp
- a creation timestamp

Invitation tokens are secrets and are therefore stored as hashes rather than raw tokens.

An invitation is associated with one organisation and establishes the organisation and role of the account created from it. The recipient chooses their password during account setup.

Invitations are intended to be one-time credentials. An invitation must not be usable after it has been used or after its expiry time.

## 8. Adopter profile model

The `adopter_profiles` table stores the current lifestyle information for an adopter.

An adopter profile belongs to exactly one user, and each adopter user can have at most one profile.

The profile contains structured information used by the matching system:

- home type
- outdoor space
- activity level
- whether children live in the household
- whether dogs already live in the household
- whether cats already live in the household
- adopter experience level
- time available for the animal
- creation and update timestamps

These values describe the adopter's current situation. They are not historical application records.

The profile does not use an `UNKNOWN` value for these self-reported fields. The profile is considered complete only when the required lifestyle information has been provided.

## 9. Adopter preference data

Some adopter preferences are multi-select values and are therefore stored in separate relationship tables rather than as comma-separated or JSON fields.

### 9.1 Preferred species

The `adopter_preferred_species` table associates an adopter profile with one or more preferred species.

Its composite primary key consists of:

- `adopter_profile_id`
- `species`

The supported species in the MVP are `DOG` and `CAT`.

### 9.2 Preferred sizes

The `adopter_preferred_sizes` table associates an adopter profile with one or more preferred animal sizes.

Its composite primary key consists of:

- `adopter_profile_id`
- `size`

The supported sizes are `SMALL`, `MEDIUM`, and `LARGE`.

### 9.3 Child age groups

The `adopter_child_age_groups` table associates an adopter profile with one or more child age groups relevant to matching.

Its composite primary key consists of:

- `adopter_profile_id`
- `child_age_group`

The supported groups are:

- `YOUNG_CHILDREN`
- `SCHOOL_AGE_CHILDREN`
- `TEENAGERS`

These relationship tables make multi-select preferences explicit and allow the matching service to query them without parsing unstructured values.

## 10. Profile ownership and matching

The authenticated user is the authority for their own current adopter profile.

The backend derives the profile from the authenticated session rather than accepting an arbitrary adopter profile ID from the client for profile management.

The matching service reads the current adopter profile and its preference relationships when calculating potential matches.

Changing the current profile may therefore change future matching results.

Historical application snapshots are separate from this current profile and must not be rewritten when the profile changes.

## 11. Animal model

The `animals` table stores the core information used to display animals, support discovery, calculate potential matches, and manage the adoption lifecycle.

Each animal has:

- a UUID primary key
- name
- species
- age value
- age unit
- the date on which the recorded age information was assessed
- sex
- size
- facility foreign key
- energy level
- personality description
- children compatibility
- dog compatibility
- cat compatibility
- suitable home type
- outdoor space requirement
- experience requirement
- animal description
- adoption status
- creation and update timestamps

The MVP supports dogs and cats only.

Animal age is represented by an age value and an age unit rather than a single fixed unit. The age value must be zero or greater.

The `age_recorded_at` field records when the recorded age information was assessed. It is intended to be updated when the recorded age information changes rather than on every unrelated animal update.

## 12. Animal compatibility data

Compatibility information is stored as structured fields so that it can be used consistently by discovery filters and the matching service.

Trait-like compatibility fields include:

- compatibility with children
- compatibility with dogs
- compatibility with cats
- suitable home type
- outdoor space requirement
- experience requirement
- energy level

Where the available information is genuinely unknown, the relevant animal attributes may use their defined `UNKNOWN` value.

Unknown animal information must not automatically be treated as compatible by the matching system.

Together with the adopter profile, these fields provide the structured inputs required for deterministic hard-constraint and soft-factor matching.

## 13. Personality traits

Personality traits are represented using two tables: `personality_traits` and `animal_personality_traits`.

The `personality_traits` table stores reusable named traits.

Each personality trait has:

- a UUID primary key
- a unique name

The `animal_personality_traits` table creates a many-to-many relationship between animals and personality traits.

Its composite primary key consists of:

- `animal_id`
- `personality_trait_id`

An animal can therefore have multiple personality traits, and the same trait can be associated with multiple animals.

## 14. Animal photos

The `animal_photos` table stores photos associated with an animal.

Each photo has:

- a UUID primary key
- an animal foreign key
- an image URL
- a flag indicating whether it is the primary photo
- a display order

The display order must be zero or greater.

Together with the animal relationship, the database enforces that an animal can have at most one primary photo.

Photo storage itself is represented by a URL in the current model. The exact media storage and upload workflow are outside the current data-model implementation scope.

## 15. Animal status and lifecycle

An animal has an explicit adoption status.

The supported statuses are:

- `AVAILABLE`
- `ADOPTION_PENDING`
- `ADOPTED`
- `UNAVAILABLE`

Discovery operates on the animal status and excludes animals that are no longer available for adoption.

Application and adoption workflows may change the animal status according to the application state and adoption rules. These transitions are enforced by backend services rather than by treating the animal status as a client-controlled value.

## 16. Favourite model

The `favourites` table represents an adopter saving an animal for later consideration.

The current implementation associates a favourite with an `adopter_profile_id` and an `animal_id`.

The composite primary key consists of:

- `adopter_profile_id`
- `animal_id`

This prevents the same adopter profile from creating duplicate favourite records for the same animal.

Each favourite also records its creation timestamp.

A favourite is not an application, reservation, or indication that an animal has been selected for adoption.

Adding or removing a favourite must not change the animal's adoption status or availability.

The authenticated adopter is identified by the backend session and resolved to their adopter profile. The client does not choose another adopter profile when managing favourites.

## 17. Application model

The `applications` table represents an adopter's formal application to adopt a specific animal.

An application belongs to:

- one adopter profile
- one animal

The application has a UUID primary key and records its current workflow status and submission/update timestamps.

The intended application content includes:

- reason for adoption
- care plan
- additional information

These fields represent information supplied by the applicant rather than server-controlled workflow data.

The current implementation stores these three application fields directly on `applications`. The application submission workflow still needs to populate them from validated applicant input and enforce the complete application workflow.

The application status is controlled by the backend state machine. Clients must not be able to assign arbitrary application statuses.

## 18. Application profile snapshot

An application must preserve the relevant adopter profile information that existed when the application was submitted.

The purpose of the snapshot is to allow the rescue organisation to understand the information on which the application was originally submitted, even if the adopter later changes their current profile.

The snapshot should contain the relevant scalar lifestyle fields from the adopter profile, together with the relevant multi-select preference data.

The intended relational snapshot data is represented through:

- application preferred species
- application preferred sizes
- application child age groups

The current preferred-species, preferred-size, and child-age-group application relationship tables provide the structure for these immutable relationships.

The current database implementation contains the required scalar application snapshot fields on `applications`. The application submission workflow must populate these fields from the adopter's current profile and preserve them as historical data.

Snapshot data is historical application data. Updating the adopter's current profile must never rewrite an existing application snapshot.

## 19. Application status history

The `application_status_history` table records changes to an application's workflow state.

Each history entry belongs to one application and records the resulting application status.

The intended history record contains:

- a UUID primary key
- application foreign key
- resulting application status
- the time of the change
- the authenticated user who made the change
- an optional reason

History is append-only from the API perspective. A later status change creates a new history entry rather than modifying an earlier entry.

Together, the application and its status history provide both the current workflow state and the historical sequence of state changes.

The current implementation stores `note`, `created_at`, and `changed_by`, which records the authenticated user responsible for the status change. The application service and API workflow must still ensure that history entries are created consistently for valid status transitions.

## 20. Database constraints and indexes

The database is responsible for structural integrity. Application services remain responsible for business rules that require contextual decisions.

The current and intended constraints include:

- primary keys on all main entities
- foreign keys between related entities
- unique email addresses for users
- unique personality trait names
- one-to-one enforcement between a user and their adopter profile
- composite primary keys on adopter preference relationship tables
- composite primary keys on application preference snapshot relationship tables
- non-negative animal age values
- non-negative animal photo display orders
- at most one primary photo per animal
- role and organisation consistency for users

The current PostgreSQL schema already implements the structural constraints represented in the current SQLAlchemy models and migration.

The application workflow also requires an active-application uniqueness rule so that concurrent requests cannot create duplicate active applications for the same adopter and animal.

The intended rule is a partial unique database index covering the adopter/animal relationship for active application statuses only. This allows historical terminal applications while preventing multiple active applications for the same animal.

The current PostgreSQL migration implements this rule as a partial unique index covering the adopter/animal relationship for active application statuses only. The application service must still handle the resulting constraint safely when concurrent submissions occur.

## 21. PostgreSQL enum types

The application uses PostgreSQL enum types for stable domain values represented by Python enums.

Examples include:

- user roles
- account status
- animal species
- animal sex
- animal size
- age units
- energy levels
- compatibility values
- suitable home types
- outdoor space requirements
- experience requirements
- animal status
- application status
- adopter home and lifestyle values
- child age groups

Using database enums provides structural protection against invalid values and keeps the database representation aligned with the application domain.

Enum changes should therefore be treated as schema changes and managed through Alembic migrations rather than by changing Python enum definitions alone.

## 22. Matching data requirements

The matching system uses structured data from both the adopter and animal sides.

Adopter inputs include:

- home type
- outdoor space
- activity level
- children in the household
- existing dogs
- existing cats
- experience level
- time available
- preferred species
- preferred sizes
- child age groups

Animal inputs include:

- species
- size
- age
- energy level
- children compatibility
- dog compatibility
- cat compatibility
- suitable home type
- outdoor space requirement
- experience requirement
- personality traits where relevant to the matching rules

The database stores these inputs as structured values so the matching service can apply deterministic rules without parsing free-text descriptions.

Unknown animal information is represented explicitly where supported by the domain model. The matching service must not silently convert unknown information into a positive compatibility result.

The database does not calculate match scores. Match scoring, hard constraints, match levels, and explanations belong to the backend matching service.

## 23. Application snapshot relationship tables

Application preference snapshots are stored separately from the adopter's current preference relationships.

The snapshot relationship tables are:

- `application_preferred_species`
- `application_preferred_sizes`
- `application_child_age_groups`

Each relationship is tied to a specific application rather than to the current adopter profile.

For example, changing an adopter's preferred species after submitting an application must not change the species preferences recorded for that existing application.

Together with the required scalar snapshot fields on `applications`, these tables provide the historical profile state required by the application workflow.

## 24. Current implementation alignment

The current SQLAlchemy models and Alembic migration implement the core relational foundation of the data model.

Currently implemented database structures include:

- users and role-based account data
- rescue organisations
- facilities
- organisation invitations
- adopter profiles
- adopter preference relationships
- animals
- personality traits and animal personality relationships
- animal photos
- favourites
- applications
- application preference relationships
- application status history

The current implementation also includes PostgreSQL foreign keys, primary keys, unique constraints, check constraints, native enum types, and the partial unique index that prevents multiple primary photos for the same animal.

The following areas still require implementation alignment with the intended model:

- application scalar fields for `reason_for_adoption`, `care_plan`, and `additional_information`
- scalar adopter profile snapshot fields on applications
- immutable persistence of application snapshot data during submission
- actor information on application status-history records
- the active-application partial unique index required for concurrent application submissions

These gaps do not change the intended domain model. They identify database structures that must be brought into alignment before the corresponding application workflows are considered complete.

The current implementation uses `adopter_profile_id` for favourites and applications. This makes the adopter profile the direct domain relationship for those records while the authenticated user remains the account-level identity. The backend resolves the current adopter profile from the authenticated user session.

## 25. Deliberate exclusions

The following data structures are intentionally outside the MVP data model:

- breed as a required animal field
- latitude and longitude
- geospatial points or polygons
- radius-based location search
- PostGIS-specific spatial structures
- donations and payment data
- messaging data
- notification infrastructure
- lost-pet records
- social interaction data
- machine-learning model metadata
- complex analytics warehouses
- separate service-specific databases

These exclusions keep the database focused on the core adoption workflow while leaving room for future expansion if product requirements justify it.

## 26. Data integrity boundary

PostgreSQL is responsible for structural integrity such as:

- primary keys
- foreign keys
- uniqueness
- required fields
- value constraints
- enum values
- relationship integrity

Backend services are responsible for contextual business rules such as:

- application state transitions
- adoption completion workflows
- profile completeness
- animal availability checks
- organisation authorisation
- matching rules
- invitation validity
- application submission rules

Treating these responsibilities separately prevents business workflows from being hidden inside database structure while still using the database to protect fundamental data integrity.

## 27. Related documentation

- `docs/product/requirements.md` - product and acceptance requirements
- `docs/product/product-overview.md` - product purpose, users, scope, and boundaries
- `docs/architecture/architecture.md` - system architecture and responsibility boundaries
- `docs/architecture/api-design.md` - REST API contract and workflow design
- `docs/architecture/technology-decisions.md` - technology choices and engineering reasoning
- `docs/engineering/security.md` - security engineering decisions and controls
- `docs/decisions/decision-log.md` - historical project decisions
