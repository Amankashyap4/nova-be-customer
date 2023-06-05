import enum


class AccountStatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"
    first_time = "first_time"
    disabled = "disabled"


class IDEnum(enum.Enum):
    national_id = "national_id"
    drivers_license = "drivers_license"
    passport = "passport"
    voters_id = "voters_id"
    null = "null"


class RegularExpression(enum.Enum):
    phone_number = r"((\+?233)((2)[03467]|(5)[045679])\d{7}$)|(((02)[03467]|(05)[045679])\d{7}$)"  # noqa
    pin = r"([0-9]{4}$)"
    token = r"([0-9]{6}$)"

class Cylinder_quality(enum.Enum):
  very_bad = "very_bad"
  bad = "bad"
  good = "good"
  average = "average"
  excellent = "excellent"
  null = "null"

class CylinderType(enum.Enum):
    steel = "steel"
    composite = "composite"


class CylinderSize(enum.Enum):
    three_kg = "three_kg"
    six_kg = "six_kg"
    twelve_kg = "twelve_kg"
