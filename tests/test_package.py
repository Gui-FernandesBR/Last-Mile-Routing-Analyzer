import pytest


def test_print_info(example_package_1):
    assert example_package_1.print_info() == None


def test_modify_status(example_package_1):
    assert example_package_1.modify_status("delivered") == None
    assert example_package_1.status == "delivered"


def test_invalid_status(example_package_1):
    with pytest.raises(ValueError):
        example_package_1.modify_status("invalid status")
