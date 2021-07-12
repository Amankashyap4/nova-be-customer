import enum


class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"
    first_time = "first_time"


class IDEnum(enum.Enum):
    national_id = "national_id"
    drivers_license = "drivers_license"
    passport = "passport"
    voters_id = "voters_id"
