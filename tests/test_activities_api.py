import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    test_activities = {
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@example.edu"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Wednesdays",
            "max_participants": 18,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client: TestClient) -> None:
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == ["existing@example.edu"]
    assert response.json()["Art Club"]["participants"] == []


def test_signup_adds_participant_and_is_visible_in_activities(client: TestClient) -> None:
    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": "new@example.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@example.edu for Art Club"}
    assert "new@example.edu" in client.get("/activities").json()["Art Club"]["participants"]


def test_signup_returns_404_for_unknown_activity(client: TestClient) -> None:
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "new@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_participant(client: TestClient) -> None:
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant_from_activities(client: TestClient) -> None:
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Unregistered existing@example.edu from Chess Club"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == []


def test_unregister_returns_404_for_unknown_activity(client: TestClient) -> None:
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_unregistered_participant(client: TestClient) -> None:
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "missing@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"