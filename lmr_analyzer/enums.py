from enum import Enum


class BaseEnum(Enum):

    @classmethod
    def get_members(cls):
        return [member.value for member in cls]


class DistanceMode(BaseEnum):
    HAVERSINE = "haversine"
    OSM = "osm"
    OSMNX = "osmnx"
    GMAPS = "gmaps"


class LocationType(BaseEnum):
    DEPOT = "depot"
    PICKUP = "pickup"
    DELIVERY = "delivery"


class PackageStatus(BaseEnum):
    TO_BE_DELIVERED = "to-be-delivered"
    REJECTED = "rejected"
    ATTEMPTED = "attempted"
    DELIVERED = "delivered"
