from datetime import datetime

import pytest

from lmr_analyzer.package import Package
from lmr_analyzer.stop import Stop


@pytest.fixture
def example_package_1() -> Package:
    return Package(
        name="package_1",
        dimensions=(1, 1, 1),
        status="delivered",
        weight=0.5,
        price=10,
    )


@pytest.fixture
def example_package_2() -> Package:
    return Package(
        name="package_2",
        dimensions=(1, 1, 1),
        status="delivered",
        weight=0.5,
        price=10,
    )


@pytest.fixture
def example_stop(example_package_1, example_package_2) -> Stop:
    return Stop(
        name="example_stop",
        location=(0, 0),
        location_type="delivery",
        time_window=(datetime(2022, 11, 20, 10), datetime(2022, 11, 20, 12)),
        packages=[example_package_1, example_package_2],
    )
