from backend.app.core.enums import ApplicationStatus, Species


def test_species_values():
    assert Species.DOG.value == "DOG"
    assert Species.CAT.value == "CAT"


def test_application_status_values():
    assert ApplicationStatus.SUBMITTED.value == "SUBMITTED"
    assert ApplicationStatus.APPROVED.value == "APPROVED"
    assert ApplicationStatus.ADOPTED.value == "ADOPTED"
    assert ApplicationStatus.DECLINED.value == "DECLINED"