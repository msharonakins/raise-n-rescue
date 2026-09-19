from enum import Enum


class UserRole(str, Enum):
    ADOPTER = "ADOPTER"
    RESCUE_STAFF = "RESCUE_STAFF"


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class Species(str, Enum):
    DOG = "DOG"
    CAT = "CAT"


class Sex(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class Size(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"


class AgeUnit(str, Enum):
    WEEKS = "WEEKS"
    MONTHS = "MONTHS"
    YEARS = "YEARS"


class EnergyLevel(str, Enum):
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Compatibility(str, Enum):
    UNKNOWN = "UNKNOWN"
    COMPATIBLE = "COMPATIBLE"
    NOT_COMPATIBLE = "NOT_COMPATIBLE"


class SuitableHomeType(str, Enum):
    UNKNOWN = "UNKNOWN"
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"
    EITHER = "EITHER"


class OutdoorSpaceRequirement(str, Enum):
    UNKNOWN = "UNKNOWN"
    NOT_REQUIRED = "NOT_REQUIRED"
    PREFERRED = "PREFERRED"
    REQUIRED = "REQUIRED"


class ExperienceRequirement(str, Enum):
    UNKNOWN = "UNKNOWN"
    NO_EXPERIENCE_REQUIRED = "NO_EXPERIENCE_REQUIRED"
    SOME_EXPERIENCE_PREFERRED = "SOME_EXPERIENCE_PREFERRED"
    EXPERIENCED_OWNER_REQUIRED = "EXPERIENCED_OWNER_REQUIRED"


class AnimalStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    ADOPTION_PENDING = "ADOPTION_PENDING"
    ADOPTED = "ADOPTED"
    UNAVAILABLE = "UNAVAILABLE"


class ApplicationStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    HOME_CHECK = "HOME_CHECK"
    APPROVED = "APPROVED"
    ADOPTED = "ADOPTED"
    DECLINED = "DECLINED"
    WITHDRAWN = "WITHDRAWN"
    CLOSED_ANIMAL_ADOPTED = "CLOSED_ANIMAL_ADOPTED"


class HomeType(str, Enum):
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"


class OutdoorSpace(str, Enum):
    NONE = "NONE"
    LIMITED = "LIMITED"
    AVAILABLE = "AVAILABLE"


class ActivityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class YesNo(str, Enum):
    YES = "YES"
    NO = "NO"


class ExperienceLevel(str, Enum):
    FIRST_TIME = "FIRST_TIME"
    SOME_EXPERIENCE = "SOME_EXPERIENCE"
    EXPERIENCED = "EXPERIENCED"


class TimeAvailable(str, Enum):
    LESS_THAN_1_HOUR = "LESS_THAN_1_HOUR"
    ONE_TO_TWO_HOURS = "ONE_TO_TWO_HOURS"
    TWO_TO_FOUR_HOURS = "TWO_TO_FOUR_HOURS"
    FOUR_PLUS_HOURS = "FOUR_PLUS_HOURS"


class ChildAgeGroup(str, Enum):
    YOUNG_CHILDREN = "YOUNG_CHILDREN"
    SCHOOL_AGE_CHILDREN = "SCHOOL_AGE_CHILDREN"
    TEENAGERS = "TEENAGERS"
