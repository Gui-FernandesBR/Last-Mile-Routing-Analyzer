__author__ = "Guilherme Fernandes Alves"

from .package import package as package_class
from .route import route as route_class
from .stop import stop as stop_class
from .vehicle import vehicle as vehicle_class
from datetime import datetime
import pytz


class amz_serializer:
    """A serializer for the Amazon data. The serializer is used to convert the
    Amazon data into a format that can be used by the LMR algorithm.
    """

    def __init__(self):
        return None

    def serialize_package(packages_dict):
        """Serializes a package object into a dictionary. The dictionary can be
        used to create a new package object for each package present in the
        packages_dict.

        Parameters
        ----------
        packages_dict : dict
            A dictionary containing the packages to be serialized. The dictionary
            must be in the form ...

        Returns
        -------
        dict
            A dictionary containing the serialized packages. The dictionary is
            in the form ...

        Raises
        ------
        ValueError
            If the packages_dict is not in the correct format.
        """

        for index1, route_id in enumerate(packages_dict):
            for index2, stop_id in enumerate(packages_dict[route_id]):
                # Iterate through the packages in the current stop
                for package_id, values in packages_dict[route_id][stop_id].items():

                    if isinstance(values, package_class):
                        continue

                    else:
                        if values["scan_status"] == "DELIVERED":
                            status = "delivered"
                        elif values["scan_status"] == "REJECTED":
                            status = "rejected"
                        elif values["scan_status"] == "DELIVERY_ATTEMPTED":
                            status = "attempted"
                        else:
                            raise ValueError(
                                f"Invalid package status. Please check {values['scan_status']}"
                            )

                        # Create one package object
                        pck = package_class(
                            name=package_id,
                            dimensions=(
                                values["dimensions"]["depth_cm"],
                                values["dimensions"]["height_cm"],
                                values["dimensions"]["width_cm"],
                            ),
                            status=status,
                            weight=None,
                            price=None,
                        )

                        # Add the package to the package dictionary
                        packages_dict[route_id][stop_id][package_id] = pck

        # 'PackageID_'
        # scan_status
        # time_window[start_time_utc, end_time_utc]
        # planned_service_time_seconds
        # dimensions[depth_cm, height_cm, width_cm]

        return packages_dict

    def serialize_route(routes_dict, packages_dict):
        """Serializes a route object into a dictionary. The dictionary can be
        used to create a new route object for each route present in the
        routes_dict.

        Parameters
        ----------
        routes_dict : dict
            A dictionary containing the routes to be serialized. The dictionary
            must be in the form ...

        Returns
        -------
        dict
            A dictionary containing the serialized routes. The dictionary is
            in the form ...

        Raises
        ------
        ValueError
            If the routes_dict is not in the correct format.
        """

        for index1, route_id in enumerate(routes_dict):
            if isinstance(routes_dict[route_id], route_class):
                continue

            for index2, stop_id in enumerate(routes_dict[route_id]["stops"]):

                if isinstance(routes_dict[route_id]["stops"][stop_id], stop_class):
                    continue

                lc_type = routes_dict[route_id]["stops"][stop_id]["type"]
                if lc_type == "Dropoff":
                    lc_type = "delivery"
                elif lc_type == "Station":
                    lc_type = "depot"
                else:
                    raise ValueError(f"Invalid location type, please check {lc_type}")

                stop = stop_class(
                    name=stop_id,
                    location=(
                        routes_dict[route_id]["stops"][stop_id]["lat"],
                        routes_dict[route_id]["stops"][stop_id]["lng"],
                    ),
                    location_type=lc_type,
                    time_window=(0, 0),
                    planned_service_time=0,
                    packages=packages_dict[route_id][stop_id],
                )

                routes_dict[route_id]["stops"][stop_id] = stop

            vehicle = vehicle_class(
                name="random_vehicle",
                capacity=routes_dict[route_id]["executor_capacity_cm3"],
            )

            date = [int(x) for x in routes_dict[route_id]["date_YYYY_MM_DD"].split("-")]
            hour = [
                int(x) for x in routes_dict[route_id]["departure_time_utc"].split(":")
            ]
            route = route_class(
                name=route_id,
                stops=routes_dict[route_id]["stops"],
                departure_time=datetime(
                    date[0], date[1], date[2], hour[0], hour[1], hour[2], 0, pytz.UTC
                ),
                vehicle=vehicle,
            )

            routes_dict[route_id] = route

        return routes_dict

    def serialize_actual_sequences(actual_sequences):

        for route_id, route_dict in actual_sequences.items():
            if isinstance(route_dict, list):
                continue
            for _, ac_dict in route_dict.items():
                sorted_ac_dict = {
                    k: v for k, v in sorted(ac_dict.items(), key=lambda item: item[1])
                }
                sequence_names = list(sorted_ac_dict.keys())
                actual_sequences[route_id] = sequence_names

        return actual_sequences

    def serialize_travel_times(travel_times):
        pass
