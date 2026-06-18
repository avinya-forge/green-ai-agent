from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database import Base
from src.core.models import User, Team, TeamMembership, ProjectDB

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module(module):
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    Base.metadata.drop_all(bind=engine)


def test_create_and_read_user():
    db = TestingSessionLocal()
    user = User(email="test@example.com", full_name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"

    fetched_user = db.query(User).filter(User.email == "test@example.com").first()
    assert fetched_user is not None
    assert fetched_user.full_name == "Test User"
    db.close()


def test_create_team_and_membership():
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "test@example.com").first()

    team = Team(name="Engineering Team")
    db.add(team)
    db.commit()
    db.refresh(team)

    assert team.id is not None

    membership = TeamMembership(user_id=user.id, team_id=team.id, role="admin")
    db.add(membership)
    db.commit()

    fetched_team = db.query(Team).filter(Team.name == "Engineering Team").first()
    assert len(fetched_team.members) == 1
    assert fetched_team.members[0].user_id == user.id
    db.close()


def test_create_project_for_team():
    db = TestingSessionLocal()
    team = db.query(Team).filter(Team.name == "Engineering Team").first()

    project = ProjectDB(name="Green-AI Migration", team_id=team.id)
    db.add(project)
    db.commit()
    db.refresh(project)

    assert project.id is not None
    assert project.team_id == team.id

    fetched_team = db.query(Team).filter(Team.name == "Engineering Team").first()
    assert len(fetched_team.projects) == 1
    assert fetched_team.projects[0].name == "Green-AI Migration"
    db.close()
