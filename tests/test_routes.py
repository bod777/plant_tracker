import os
import types
from bson import ObjectId

import pytest
from fastapi.testclient import TestClient

# Set environment variables and stub optional dependencies **before** importing app modules
os.environ.setdefault("PLANT_ID_API_KEY", "test")
import sys
sys.modules['pandas'] = types.ModuleType('pandas')
bs4_stub = types.ModuleType('bs4')
bs4_stub.BeautifulSoup = object
sys.modules['bs4'] = bs4_stub

from server.app.routers.auth import deps
from server.app import main
from server.app.routers import plants as plants_router


class DummyCursor:
    def __init__(self, docs):
        self._docs = docs

    async def to_list(self, length):
        return self._docs[:length]


class DummyCollection:
    def __init__(self, docs=None):
        self.docs = docs or []

    async def insert_one(self, doc):
        self.docs.append(doc)
        return types.SimpleNamespace(inserted_id="1")

    def find(self, query, projection=None):
        filtered = [d for d in self.docs if all(d.get(k) == v for k, v in query.items())]
        return DummyCursor(filtered)

    async def find_one(self, query, projection=None):
        for d in self.docs:
            if all(d.get(k) == v for k, v in query.items()):
                return d
        return None

    async def update_one(self, filter_, update):
        matched = 0
        for d in self.docs:
            if all(d.get(k) == v for k, v in filter_.items()):
                matched = 1
                for k, v in update.get("$set", {}).items():
                    d[k] = v
        return types.SimpleNamespace(matched_count=matched)

    async def delete_one(self, filter_):
        before = len(self.docs)
        self.docs = [d for d in self.docs if not all(d.get(k) == v for k, v in filter_.items())]
        deleted = before - len(self.docs)
        return types.SimpleNamespace(deleted_count=deleted)

    async def create_index(self, *args, **kwargs):
        pass


class DummyUsers:
    async def create_index(self, *args, **kwargs):
        pass


class DummyClientAdmin:
    async def command(self, *args, **kwargs):
        pass


class DummyClient:
    def __init__(self):
        self.admin = DummyClientAdmin()


class DummyDB:
    def __init__(self, records=None, infos=None, plants=None):
        self.client = DummyClient()
        self.plantRecord = DummyCollection(records)
        self.plantInfo = DummyCollection(infos)
        self.plants = DummyCollection(plants)
        self.users = DummyUsers()


@pytest.fixture
def client(monkeypatch):
    record_docs = [{"recordId": "r1", "userId": "user1", "plants": [], "photos": [], "location": [0.0, 0.0]}]
    info_docs = [{"plantId": "p1", "source": "plant_id", "photos": []}]
    plant_docs = [{"_id": ObjectId("507f1f77bcf86cd799439011"), "user_id": "user1"}]
    fake_db = DummyDB(record_docs, info_docs, plant_docs)
    monkeypatch.setattr(plants_router, "db", fake_db)
    monkeypatch.setattr(main, "db", fake_db)
    main.app.dependency_overrides[deps.get_current_user] = lambda: {
        "userId": "user1",
        "email": "test@example.com",
    }
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()


def test_auth_me(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json() == {"email": "test@example.com", "userId": "user1"}


def test_logout(client):
    resp = client.post("/api/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Logged out"
    assert "access_token=" in resp.headers.get("set-cookie", "")


def test_get_plant_records(client):
    resp = client.get("/api/plant-records")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if data:
        assert "recordId" in data[0]


def test_get_plant_info(client):
    resp = client.get("/api/plant-info/p1")
    assert resp.status_code == 200
    assert resp.json()["plantId"] == "p1"


def test_delete_plant(client):
    resp = client.delete("/api/plants/507f1f77bcf86cd799439011")
    assert resp.status_code == 200
    assert resp.json()["id"] == "507f1f77bcf86cd799439011"


def test_delete_plant_not_found(client, monkeypatch):
    empty_db = DummyDB([], [], [])
    monkeypatch.setattr(plants_router, "db", empty_db)
    monkeypatch.setattr(main, "db", empty_db)
    with TestClient(main.app) as c:
        main.app.dependency_overrides[deps.get_current_user] = lambda: {
            "userId": "user1",
            "email": "test@example.com",
        }
        resp = c.delete("/api/plants/507f1f77bcf86cd799439011")
    main.app.dependency_overrides.clear()
    assert resp.status_code == 404

