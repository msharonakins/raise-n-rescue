import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationSubmissionData:
    animal_id: uuid.UUID
    reason_for_adoption: str
    care_plan: str
    additional_information: str | None = None
