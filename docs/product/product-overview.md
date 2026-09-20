# Product Overview

## What I'm building

Raise 'n Rescue is an animal adoption platform focused on helping prospective adopters understand which animals may fit their circumstances and making the adoption process easier to navigate.

The product covers two connected problems:

1. Before applying: "Could this animal be compatible with my lifestyle and situation?"
2. After applying: "What is happening with my application?"

The first problem is addressed through structured animal information, adopter lifestyle information and deterministic compatibility guidance.

The second is addressed through an adoption application workflow with clear statuses and status history.

The platform is designed to support adoption decisions rather than make them. Matching provides guidance about potential compatibility. It does not approve, reject or reserve animals.

## Target users

### Prospective adopters

The primary users are people considering adopting an animal.

They need to be able to:

- discover available animals;
- filter animals using relevant characteristics;
- understand an animal's needs and compatibility information;
- maintain their own lifestyle and household information;
- see which animals may be potential matches;
- understand why a potential match was produced;
- save animals for later consideration;
- submit adoption applications;
- track application progress and history.

### Rescue staff

The secondary users are staff members working for rescue organisations.

They need to be able to:

- manage animals belonging to their organisation;
- maintain animal information relevant to compatibility;
- review adoption applications;
- update application statuses;
- manage the adoption workflow;
- complete an adoption while keeping the application's history consistent.

Rescue staff access is organisation-scoped. A staff member must not be able to manage or view another organisation's operational data.

## Product journey

The main adopter journey is:

**DISCOVER -> UNDERSTAND -> MATCH -> CONSIDER -> APPLY -> TRACK -> ADOPT**

### Discover

An adopter browses available dogs and cats and narrows the list using relevant filters.

### Understand

The adopter opens an animal profile and reviews information such as age, size, energy level, personality, compatibility with children and other animals, home requirements and experience requirements.

### Match

The adopter can use their lifestyle profile to see animals that may be compatible with their circumstances.

The matching process is deterministic and explainable. The system should be able to show the factors that contributed to a result.

### Consider

The adopter can save animals as favourites while deciding which animals they want to consider further.

A favourite does not reserve an animal.

### Apply

The adopter submits an application for an available animal and provides the information required by the application workflow.

A matching result is not required in order to apply. An adopter can apply to an animal they are interested in even if the matching system does not identify it as a potential match.

### Track

After submission, the adopter can see the current application status and the history of status changes.

### Adopt

When a rescue organisation completes an adoption, the animal and related applications must move to the appropriate final states as part of the adoption workflow.

## MVP scope

The MVP supports dogs and cats and includes:

1. Animal browsing and filtering
2. Detailed animal profiles
3. Adopter lifestyle profiles
4. Deterministic potential matching
5. Favourites
6. Adoption applications
7. Application status tracking and history
8. Basic rescue-side management
9. Authentication and role-based access

The MVP is intended to demonstrate the complete core workflow rather than provide every possible feature an adoption platform could eventually support.

## Matching philosophy

Matching is a decision-support feature.

The system uses structured information about the animal and adopter to identify potential compatibility. The result should be understandable rather than being an unexplained score.

The matching system must:

- use deterministic rules;
- produce the same result for the same inputs;
- distinguish hard incompatibilities from softer preferences;
- explain relevant matching factors;
- treat unknown animal information carefully;
- never automatically approve or reject an adoption application;
- never reserve an animal;
- never prevent an adopter from browsing animals outside their matches.

The product language should use terms such as **Potential match** and **Strong potential match** rather than claiming that an animal is definitely suitable.

A potential match is only guidance. The final adoption decision remains with the adopter and rescue organisation.

Machine-learning matching is deliberately deferred until there is enough real structured data and adoption outcome data to evaluate whether it would provide meaningful value.

## Adoption workflow

The application workflow is designed to represent the actual progression of an adoption application rather than treating an application as a single static record.

The MVP application states are:

- `SUBMITTED`
- `UNDER_REVIEW`
- `HOME_CHECK`
- `APPROVED`
- `ADOPTED`
- `DECLINED`
- `WITHDRAWN`
- `CLOSED_ANIMAL_ADOPTED`

Applications can only move through defined transitions.

When an adoption is completed:

1. the successful application becomes `ADOPTED`;
2. the animal becomes `ADOPTED`;
3. other active applications for that animal become `CLOSED_ANIMAL_ADOPTED`;
4. the relevant status history is recorded.

This keeps the animal and application state consistent.

## Rescue organisation model

Rescue organisations are treated as separate operational boundaries.

A rescue organisation can have:

- rescue staff accounts;
- facilities;
- animals;
- adoption applications associated with its animals.

Staff accounts are not created through an unrestricted public rescue registration flow.

The intended onboarding model uses controlled organisation invitations. An invitation identifies the organisation and role, and the recipient completes account setup through that invitation.

This reduces the risk of arbitrary users creating rescue staff accounts or assigning themselves to an organisation.

## Location

Animals have a location through their rescue facility and facility address information.

The MVP does not implement geospatial search, radius filtering, maps or distance-based matching.

Location-aware discovery can be added later if there is a clear product need and an appropriate data model for it.

## Product boundaries

Raise 'n Rescue is not intended to:

- make the adoption decision for a person;
- guarantee that an animal will be suitable;
- automatically approve or reject applications;
- reserve animals through favourites or matching;
- replace the professional judgement of rescue staff;
- act as a marketplace for buying or selling animals.

The platform is intended to improve the quality of information available to adopters and make the adoption workflow easier to understand.

## Deliberately deferred features

The following features are outside the MVP:

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
- microservices;
- Kubernetes infrastructure.

These features may become relevant later, but they are not required to prove that the core product works.

## Product success criteria

For the MVP, I want the product to demonstrate that:

- an adopter can discover and understand available animals;
- an adopter can provide structured information about their lifestyle;
- the system can produce deterministic and explainable potential matches;
- an adopter can save animals and submit applications;
- an adopter can understand what happens to an application after submission;
- rescue staff can manage their organisation's animals and applications;
- application and animal states remain consistent through the adoption workflow;
- security boundaries prevent users from accessing data they should not control.

The main goal is a working end-to-end adoption workflow built on sound engineering foundations, rather than a large number of disconnected features.

