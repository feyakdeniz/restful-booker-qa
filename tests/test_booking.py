import pytest
import requests

JSON_HEADERS = {"Accept": "application/json"}


# ---------- Positive tests ----------

def test_get_all_bookings_returns_list(base_url):
    response = requests.get(f"{base_url}/booking")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0
    assert all(isinstance(item["bookingid"], int) for item in body)
    assert response.elapsed.total_seconds() < 2


def test_get_booking_returns_created_data(base_url, booking, booking_payload):
    response = requests.get(f"{base_url}/booking/{booking}", headers=JSON_HEADERS)

    assert response.status_code == 200
    assert response.json() == booking_payload


def test_update_booking_with_token(base_url, token, booking, booking_payload):
    updated = {**booking_payload, "totalprice": 400, "additionalneeds": "Dinner"}

    response = requests.put(
        f"{base_url}/booking/{booking}",
        json=updated,
        headers={**JSON_HEADERS, "Cookie": f"token={token}"},
    )

    assert response.status_code == 200
    assert response.json()["totalprice"] == 400
    assert response.json()["additionalneeds"] == "Dinner"

    # Read it back to make sure the change was really saved
    saved = requests.get(f"{base_url}/booking/{booking}", headers=JSON_HEADERS).json()
    assert saved == updated


def test_delete_booking(base_url, token, booking):
    response = requests.delete(
        f"{base_url}/booking/{booking}",
        headers={"Cookie": f"token={token}"},
    )
    # Should be 204 or 200, but the API returns 201 (see BUG-04)
    assert response.status_code in (200, 201, 204)

    # The deleted booking must no longer exist
    response = requests.get(f"{base_url}/booking/{booking}", headers=JSON_HEADERS)
    assert response.status_code == 404


# ---------- Negative tests ----------

def test_update_without_token_is_rejected(base_url, booking, booking_payload):
    response = requests.put(
        f"{base_url}/booking/{booking}",
        json={**booking_payload, "totalprice": 1},
        headers=JSON_HEADERS,
    )
    # Should be 401, but the API returns 403 (see BUG-03)
    assert response.status_code in (401, 403)

    # The booking must not have changed
    saved = requests.get(f"{base_url}/booking/{booking}", headers=JSON_HEADERS).json()
    assert saved["totalprice"] == booking_payload["totalprice"]


def test_login_with_wrong_password_returns_no_token(base_url):
    response = requests.post(
        f"{base_url}/auth",
        json={"username": "admin", "password": "wrong-password"},
    )
    assert "token" not in response.json()


@pytest.mark.xfail(reason="BUG-01: API returns 200 instead of 401", strict=True)
def test_login_with_wrong_password_returns_401(base_url):
    response = requests.post(
        f"{base_url}/auth",
        json={"username": "admin", "password": "wrong-password"},
    )
    assert response.status_code == 401
