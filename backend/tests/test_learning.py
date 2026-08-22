import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine = create_engine("sqlite:///./test_dhan_saarthi.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def register_user(email: str, name: str) -> dict:
    res = client.post("/api/auth/register", json={"full_name": name, "email": email, "password": "password123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers


def test_learn_unauthorized():
    response = client.get("/api/learn/modules")
    assert response.status_code == 401


def test_learn_catalogue_and_seeding():
    headers = register_user("learn_user1@example.com", "Learn User 1")
    res = client.get("/api/learn/modules", headers=headers)
    assert res.status_code == 200
    modules = res.json()
    assert len(modules) == 6
    module_ids = [m["module_id"] for m in modules]
    assert "savings-basics" in module_ids
    assert "digital-payment-safety" in module_ids
    assert "budgeting" in module_ids


def test_module_detail_and_invalid_id():
    headers = register_user("learn_user2@example.com", "Learn User 2")
    res_valid = client.get("/api/learn/modules/savings-basics", headers=headers)
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["module_id"] == "savings-basics"
    assert "lesson_content" in data
    assert data["status"] == "NOT_STARTED"

    res_invalid = client.get("/api/learn/modules/non-existent-module", headers=headers)
    assert res_invalid.status_code == 404


def test_start_module_and_quiz_submission():
    headers = register_user("learn_user3@example.com", "Learn User 3")

    # Start module
    res_start = client.post("/api/learn/modules/savings-basics/start", headers=headers)
    assert res_start.status_code == 200
    assert res_start.json()["status"] == "IN_PROGRESS"

    # Get Quiz Questions
    res_quiz = client.get("/api/learn/modules/savings-basics/quiz", headers=headers)
    assert res_quiz.status_code == 200
    questions = res_quiz.json()
    assert len(questions) == 3
    for q in questions:
        assert "correct_option_index" not in q  # Security check: answers must not be exposed

    # Submit correct answers: options [1, 1, 2]
    res_submit = client.post("/api/learn/modules/savings-basics/quiz", json={"answers": [1, 1, 2]}, headers=headers)
    assert res_submit.status_code == 200
    result_data = res_submit.json()
    assert result_data["score_percentage"] == 100.0
    assert result_data["correct_count"] == 3
    assert result_data["status"] == "COMPLETED"

    # Check progress summary
    res_summary = client.get("/api/learn/progress", headers=headers)
    assert res_summary.status_code == 200
    sum_data = res_summary.json()
    assert sum_data["completed_modules"] == 1
    assert sum_data["total_modules"] == 6
    assert sum_data["completion_percentage"] == 16.7


def test_personalized_recommendations_and_user_isolation():
    headers_a = register_user("learn_user_a@example.com", "User A")
    headers_b = register_user("learn_user_b@example.com", "User B")

    # User A has a critical scam scan
    client.post("/api/scam-shield/analyze", json={
        "message": "Urgent SBI account blocked! Send money to http://fake.url and enter OTP."
    }, headers=headers_a)

    # Get recommendations for User A -> Digital payment safety prioritized
    res_rec_a = client.get("/api/learn/recommendations", headers=headers_a)
    assert res_rec_a.status_code == 200
    recs_a = res_rec_a.json()
    assert len(recs_a) >= 1
    assert recs_a[0]["module_id"] == "digital-payment-safety"

    # User B has no scam scans -> Defaults prioritized
    res_rec_b = client.get("/api/learn/recommendations", headers=headers_b)
    assert res_rec_b.status_code == 200
    recs_b = res_rec_b.json()
    assert len(recs_b) >= 1
    assert recs_b[0]["module_id"] == "savings-basics"
