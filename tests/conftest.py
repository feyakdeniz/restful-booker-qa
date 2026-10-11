import os

import pytest
import requests

# The API address can be changed without touching the code, e.g.:
#   BASE_URL=https://my-test-env.example.com pytest
BASE_URL = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def token(base_url):
    """Log in once per test run and share the token with every test."""
    response = requests.post(
        f"{base_url}/auth",
        json={"username": "admin", "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def booking_payload():
    """The booking data used to create a test booking."""
    return {
        "firstname": "Feyza",
        "lastname": "Akdeniz",
        "totalprice": 250,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-12"},
        "additionalneeds": "Breakfast",
    }


@pytest.fixture
def booking(base_url, token, booking_payload):
    """Create a fresh booking for a test and delete it afterwards.

    Setup:    everything before `yield` runs before the test.
    Teardown: everything after `yield` runs after the test, even if it failed.
    """
    response = requests.post(
        f"{base_url}/booking",
        json=booking_payload,
        headers={"Accept": "application/json"},
    )
    # Should be 201 Created, but the API returns 200 (see BUG-02)
    assert response.status_code in (200, 201)
    booking_id = response.json()["bookingid"]

    yield booking_id

    # Clean up. If the test already deleted the booking, this simply fails quietly.
    requests.delete(
        f"{base_url}/booking/{booking_id}",
        headers={"Cookie": f"token={token}"},
    )
