import enum
import uuid


def gen_uuid() -> str:
    return str(uuid.uuid4())


class TransportMode(str, enum.Enum):
    kereta = "kereta"
    mobil_pribadi = "mobil_pribadi"
    pesawat = "pesawat"
    travel = "travel"
    bis = "bis"


class TripStatus(str, enum.Enum):
    draft = "draft"
    confirmed = "confirmed"


class MemberRole(str, enum.Enum):
    member = "member"
    admin = "admin"


class PlaceCategory(str, enum.Enum):
    kuliner = "kuliner"
    fun = "fun"
    sport = "sport"
    alam = "alam"


class SourceType(str, enum.Enum):
    manual = "manual"
    tiktok = "tiktok"
    youtube = "youtube"


class PlaceStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class PlanType(str, enum.Enum):
    manual = "manual"
    generated = "generated"
