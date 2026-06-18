from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.ui.app_fastapi import app
from src.core.database import Base, get_db
import pytest

from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# We need to import models here so Base knows about them before create_all
from src.core.models import User, Team, TeamMembership, ProjectDB

# Make sure tables exist initially
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    from src.core.models import User, Team, TeamMembership, ProjectDB
    # In SQLite memory DB, each engine/connection might be isolated depending on how it's handled.
    # We create tables
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_and_get_teams():
    response = client.post("/api/teams", json={"name": "Test Team", "description": "Test"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "team_id" in data

    response = client.get("/api/teams")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["teams"]) >= 1
    assert any(t["name"] == "Test Team" for t in data["teams"])


def test_create_duplicate_team():
    client.post("/api/teams", json={"name": "Unique Team"})
    response = client.post("/api/teams", json={"name": "Unique Team"})
    assert response.status_code == 400


def test_add_and_get_team_members():
    # Create team
    res = client.post("/api/teams", json={"name": "Member Team"})
    team_id = res.json()["team_id"]

    # Add member
    res = client.post(f"/api/teams/{team_id}/members", json={"user_id": "user-123", "role": "admin"})
    assert res.status_code == 200

    # Get members
    res = client.get(f"/api/teams/{team_id}/members")
    assert res.status_code == 200
    members = res.json()["members"]
    assert len(members) == 1
    assert members[0]["user_id"] == "user-123"
    assert members[0]["role"] == "admin"


def test_add_member_to_nonexistent_team():
    res = client.post("/api/teams/invalid-id/members", json={"user_id": "user-1"})
    assert res.status_code == 404


def test_get_members_from_nonexistent_team():
    res = client.get("/api/teams/invalid-id/members")
    assert res.status_code == 404
