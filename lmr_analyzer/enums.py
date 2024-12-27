from enum import Enum


class DistanceMode(Enum):
    HAVERSINE = "haversine"
    OSM = "osm"
    OSMNX = "osmnx"
    GMAPS = "gmaps"

    @staticmethod
    def get_members():
        return [member.value for member in LocationType.__members__.values()]


class LocationType(Enum):
    DEPOT = "depot"
    PICKUP = "pickup"
    DELIVERY = "delivery"

    @staticmethod
    def get_members():
        return [member.value for member in LocationType.__members__.values()]


class PackageStatus(Enum):
    TO_BE_DELIVERED = "to-be-delivered"
    REJECTED = "rejected"
    ATTEMPTED = "attempted"
    DELIVERED = "delivered"

    @staticmethod
    def get_members():
        return [member.value for member in PackageStatus.__members__.values()]
