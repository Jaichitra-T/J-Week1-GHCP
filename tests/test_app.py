from fastapi.testclient import TestClient
import pytest

from src import app

client = TestClient(app.app)

# keep a copy of original activities to restore after tests
original_activities = {k: v.copy() for k, v in app.activities.items()}


def setup_function(function):
    # reset activities to original state before each test
    app.activities.clear()
    for k, v in original_activities.items():
        # perform a shallow copy of nested dict to avoid mutation
        app.activities[k] = v.copy()


def test_root_redirects_to_index():
    response = client.get("/")
    assert response.status_code == 200
    # the TestClient follows redirects automatically
    assert "/static/index.html" in response.url.path


def test_get_activities_returns_dictionary():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_existing_activity():
    email = "newstudent@mergington.edu"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app.activities["Chess Club"]["participants"]
    assert resp.json()["message"].startswith("Signed up")


def test_signup_nonexistent_activity():
    resp = client.post("/activities/Nonexistent/signup", params={"email": "x@mergington.edu"})
    assert resp.status_code == 404


def test_double_signup_fails():
    email = "emma@mergington.edu"
    # first signup should succeed when not already in list
    resp1 = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp1.status_code == 200
    # second attempt should return 400
    resp2 = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp2.status_code == 400
