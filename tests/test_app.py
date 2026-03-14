import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    # Ensure each test sees a fresh copy of the in-memory data
    app_module.activities = copy.deepcopy(app_module._INITIAL_ACTIVITIES)


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_new_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    assert "Signed up newstudent@mergington.edu for Chess Club" in response.json()["message"]

    # Ensure participant is now listed
    response = client.get("/activities")
    assert "newstudent@mergington.edu" in response.json()["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    # Sign up once
    client.post("/activities/Chess%20Club/signup?email=dup@mergington.edu")

    # Sign up again should fail
    response = client.post("/activities/Chess%20Club/signup?email=dup@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant(client):
    # Remove an existing participant
    response = client.delete(
        "/activities/Chess%20Club/participants?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    assert "Removed michael@mergington.edu from Chess Club" in response.json()["message"]

    # Ensure participant is gone
    response = client.get("/activities")
    assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]


def test_remove_participant_not_found_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/participants?email=noone@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_nonexistent_activity_returns_404(client):
    response = client.delete(
        "/activities/DoesNotExist/participants?email=michael@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
