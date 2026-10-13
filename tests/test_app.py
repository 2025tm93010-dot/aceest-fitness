import pytest

from app import create_app


@pytest.fixture
def client():
    return create_app().test_client()


def add(client, name="Asha", plan="premium"):
    return client.post("/members", json={"name": name, "plan": plan})


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json == {"status": "ok"}


def test_plans(client):
    r = client.get("/plans")
    assert set(r.json) == {"basic", "premium", "elite"}


def test_add_member(client):
    r = add(client)
    assert r.status_code == 201
    assert r.json == {"id": 1, "name": "Asha", "plan": "premium"}


def test_add_member_default_plan(client):
    r = client.post("/members", json={"name": "Ravi"})
    assert r.json["plan"] == "basic"


def test_add_member_missing_name(client):
    assert client.post("/members", json={}).status_code == 400


def test_add_member_invalid_plan(client):
    assert add(client, plan="gold").status_code == 400


def test_list_and_get_member(client):
    add(client)
    assert len(client.get("/members").json) == 1
    assert client.get("/members/1").json["name"] == "Asha"


def test_get_missing_member(client):
    assert client.get("/members/99").status_code == 404


def test_delete_member(client):
    add(client)
    assert client.delete("/members/1").status_code == 204
    assert client.delete("/members/1").status_code == 404


def test_log_workout_and_summary(client):
    add(client)
    client.post("/members/1/workouts", json={"exercise": "squats", "minutes": 30})
    client.post("/members/1/workouts", json={"exercise": "run", "minutes": 20})
    s = client.get("/members/1/summary").json
    assert s == {"member_id": 1, "sessions": 2, "total_minutes": 50}


@pytest.mark.parametrize("payload", [
    {}, {"exercise": "run"}, {"exercise": "run", "minutes": 0},
    {"exercise": "run", "minutes": "30"}, {"minutes": 10},
])
def test_log_workout_validation(client, payload):
    add(client)
    assert client.post("/members/1/workouts", json=payload).status_code == 400


def test_workout_unknown_member(client):
    r = client.post("/members/5/workouts", json={"exercise": "run", "minutes": 5})
    assert r.status_code == 404
    assert client.get("/members/5/summary").status_code == 404
