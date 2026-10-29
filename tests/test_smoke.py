"""Testes de fumaça: a aplicação funciona de ponta a ponta."""

import pytest

from app import create_app

PASSWORD = "senha-de-teste"


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE": str(tmp_path / "test.db"),
            "SEED_PASSWORD": PASSWORD,
        }
    )
    with app.app_context():
        from app import db

        db.init_db()
    return app.test_client()


def login(client, email):
    resp = client.post("/login", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.get_json()['token']}"}


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_security_headers(client):
    resp = client.get("/health")
    assert resp.headers["Content-Security-Policy"] == "default-src 'self'"
    assert resp.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["Referrer-Policy"] == "no-referrer"


def test_login_invalid(client):
    resp = client.post("/login", json={"email": "leo@clubeaurora.com", "password": "errada"})
    assert resp.status_code == 401


def test_clients_requires_auth(client):
    assert client.get("/clients").status_code == 401


def test_list_and_search_clients(client):
    headers = login(client, "carla@clubeaurora.com")
    assert len(client.get("/clients", headers=headers).get_json()) == 5
    found = client.get("/clients/search?name=Helena", headers=headers).get_json()
    assert [c["full_name"] for c in found] == ["Helena Vasconcelos"]


def test_search_clients_rejects_sql_injection(client):
    headers = login(client, "carla@clubeaurora.com")
    found = client.get("/clients/search?name=%27%20OR%201%3D1%20--", headers=headers)
    assert found.status_code == 200
    assert found.get_json() == []


def test_bookings_flow(client):
    headers = login(client, "carla@clubeaurora.com")
    payload = {"service": "evento", "destination": "Gala", "starts_at": "2027-05-01T20:00:00", "amount": 1000}
    assert client.post("/clients/1/bookings", json=payload, headers=headers).status_code == 201
    assert len(client.get("/clients/1/bookings", headers=headers).get_json()) == 3
    assert client.get("/clients/999/bookings", headers=headers).status_code == 404


def test_admin_routes(client):
    staff = login(client, "leo@clubeaurora.com")
    admin = login(client, "armando@clubeaurora.com")
    assert client.get("/admin/users", headers=staff).status_code == 403
    assert client.get("/admin/users", headers=admin).status_code == 200
    assert client.post("/admin/users/3/role", json={"role": "admin"}, headers=staff).status_code == 403
    resp = client.post("/admin/users/3/role", json={"role": "admin"}, headers=admin)
    assert resp.status_code == 200


def test_create_user_uses_least_privileged_role(client):
    with client.application.app_context():
        from app import db

        user_id = db.create_user("novo@clubeaurora.com", PASSWORD, "Novo Cliente")
        assert db.get_user_by_id(user_id)["role"] == "client"
