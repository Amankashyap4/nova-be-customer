import enum


class StatusEnum(enum.Enum):
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


class DepositEnum(enum.Enum):
    cylinder = "cylinder"
    cash = "cash"
    cylinder_cash = "cylinder_cash"


class RegularExpression(enum.Enum):
    phone_number = r"((\+?233)((2)[03467]|(5)[045679])\d{7}$)|(((02)[03467]|(05)[045679])\d{7}$)"  # noqa
    pin = r"([0-9]{4}$)"
    token = r"([0-9]{6}$)"


def status_type():
    return [status.value for status in StatusEnum]


def id_type():
    return [user_id.value for user_id in IDEnum]


def regex_type():
    reg_exp = {exp_type.name: exp_type.value for exp_type in RegularExpression}
    return reg_exp


def deposit_type():
    return [deposit.value for deposit in DepositEnum]
