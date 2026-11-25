import os
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    def override_db():
        db = TestingSession()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

def register(client, email="test@example.com", password="password123"):
    response = client.post("/api/auth/register", json={"email":email,"full_name":"Test User","password":password})
    assert response.status_code == 201
    return response.json()["access_token"]

def auth(token): return {"Authorization": f"Bearer {token}"}


def promote(client, user_id=1, role="admin"):
    override = app.dependency_overrides[get_db]
    generator = override()
    db = next(generator)
    from app.models import User
    user = db.get(User, user_id)
    user.role = role
    db.commit()
    try: generator.close()
    except Exception: pass
