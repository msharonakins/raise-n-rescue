import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.adopter_child_age_group import AdopterChildAgeGroup
from backend.app.models.adopter_preferred_size import AdopterPreferredSize
from backend.app.models.adopter_preferred_species import AdopterPreferredSpecies
from backend.app.models.adopter_profile import AdopterProfile


class AdopterProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> AdopterProfile | None:
        statement = select(AdopterProfile).where(
            AdopterProfile.user_id == user_id
        )
        return self.session.execute(statement).scalar_one_or_none()

    def get_preferred_species(
        self,
        adopter_profile_id: uuid.UUID,
    ) -> list[AdopterPreferredSpecies]:
        statement = select(AdopterPreferredSpecies).where(
            AdopterPreferredSpecies.adopter_profile_id == adopter_profile_id
        )
        return list(self.session.execute(statement).scalars().all())

    def get_preferred_sizes(
        self,
        adopter_profile_id: uuid.UUID,
    ) -> list[AdopterPreferredSize]:
        statement = select(AdopterPreferredSize).where(
            AdopterPreferredSize.adopter_profile_id == adopter_profile_id
        )
        return list(self.session.execute(statement).scalars().all())

    def get_child_age_groups(
        self,
        adopter_profile_id: uuid.UUID,
    ) -> list[AdopterChildAgeGroup]:
        statement = select(AdopterChildAgeGroup).where(
            AdopterChildAgeGroup.adopter_profile_id == adopter_profile_id
        )
        return list(self.session.execute(statement).scalars().all())
