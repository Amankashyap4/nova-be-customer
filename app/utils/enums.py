import enum


class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"
    first_time = "first_time"


class IDEnum(enum.Enum):
    national_id = "national id"
    drivers_license = "drivers license"
    passport = "passport"
    voters_id = "voters id"
