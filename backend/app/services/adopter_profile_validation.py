from backend.app.models.adopter_profile import AdopterProfile


def is_adopter_profile_complete(
    profile: AdopterProfile,
) -> bool:
    required_fields = (
        profile.home_type,
        profile.outdoor_space,
        profile.activity_level,
        profile.children_in_household,
        profile.existing_dogs,
        profile.existing_cats,
        profile.experience_level,
        profile.time_available,
    )

    return all(value is not None for value in required_fields)
