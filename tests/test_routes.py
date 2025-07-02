import types
import pytest
from fastapi.testclient import TestClient

from server.app import routes, main, deps

class DummyCursor:
    def __init__(self, docs):
        self._docs = docs
    async def to_list(self, length):
        return self._docs[:length]

class DummyPlants:
    def __init__(self, docs=None):
        self.docs = docs or []
    async def insert_one(self, doc):
        self.docs.append(doc)
        return types.SimpleNamespace(inserted_id="1")
    def find(self, query):
        return DummyCursor(self.docs)
    async def update_one(self, filter_, update):
        matched = 1 if self.docs else 0
        return types.SimpleNamespace(matched_count=matched)
    async def create_index(self, *args, **kwargs):
        pass

class DummyClientAdmin:
    async def command(self, *args, **kwargs):
        pass

class DummyClient:
    def __init__(self):
        self.admin = DummyClientAdmin()

class DummyDB:
    def __init__(self, docs=None):
        self.client = DummyClient()
        self.plants = DummyPlants(docs)

@pytest.fixture
def client(monkeypatch):
    fake_db = DummyDB([{"_id": "abc", "user_id": "user1"}])
    monkeypatch.setattr(routes, "db", fake_db)
    monkeypatch.setattr(main, "db", fake_db)
    main.app.dependency_overrides[deps.get_current_user] = lambda: {"sub": "user1", "email": "test@example.com"}
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()

def test_auth_me(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json() == {"email": "test@example.com", "sub": "user1"}

def test_logout(client):
    resp = client.post("/api/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Logged out"
    assert "access_token=" in resp.headers.get("set-cookie", "")

def test_get_plants(client):
    resp = client.get("/api/my-plants")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_update_notes_not_found(client, monkeypatch):
    # patch db to have no docs so update_one returns matched_count=0
    empty_db = DummyDB([])
    monkeypatch.setattr(routes, "db", empty_db)
    monkeypatch.setattr(main, "db", empty_db)
    with TestClient(main.app) as c:
        main.app.dependency_overrides[deps.get_current_user] = lambda: {"sub": "user1", "email": "test@example.com"}
        resp = c.put("/api/update-plant-notes", json={"id": "507f1f77bcf86cd799439011", "notes": "hi"})
    main.app.dependency_overrides.clear()
    assert resp.status_code == 404

