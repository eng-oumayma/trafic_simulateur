import pytest

from models.route import Route
from models.vehicule import Vehicule


@pytest.fixture
def route_valide():
    return Route("R1", 100, 50, "A", "B")


@pytest.fixture
def vehicule_valide():
    return Vehicule("V1", ["R1", "R2"])