import os
import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from urls_db import Urls


TEST_DB_NAME = "test.db"
client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def manage_test_db():
    db = Urls(db_path=TEST_DB_NAME)
    app.dependency_overrides[get_db] = lambda: db
    yield
    db.close()
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)


def test_create_short_url():
    """Проверяем, что ссылка создается и возвращается корректный формат"""
    response = client.post("/shorten", json={"url": "https://google.com/"})
    assert response.status_code == 200
    assert "short_url" in response.json()
    assert "http://testserver/" in response.json()["short_url"]

def test_redirect_works():
    target_url = "https://yandex.ru/"
    res_create = client.post("/shorten", json={"url": target_url})
    short = res_create.json()["short_url"]
    code = short.split("/")[-1]

    res_redirect = client.get(f"/{code}", follow_redirects=False)
    assert res_redirect.status_code == 307
    assert res_redirect.headers["location"] == target_url

def test_non_existent_url():
    """Проверяем 404 для мусорных ссылок"""
    response = client.get("/non-existent-code")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ссылка отсутствует"
