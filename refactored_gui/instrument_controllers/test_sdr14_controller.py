from unittest.mock import Mock
from refactored_gui.instrument_controllers.sdr14_controller import SDR14
import pytest

def test_retrieve_api_invalid_filepath() -> None:

    with pytest.raises(FileNotFoundError):
        filepath = "Invalid"
        device = SDR14(filepath)

def test_retrieve_api_no_ADQ_SDK() -> None:

    with pytest.raises(WindowsError):
        device = SDR14()

def test_create_control_unit() -> None:
    assert False


def test_get_dev_info() -> None:
    assert False


def test_set_default_types() -> None:
    assert False
