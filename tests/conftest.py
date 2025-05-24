import os
from typing import Optional

import psycopg2
import pytest
from fastapi.testclient import TestClient
from src.api.app import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def clear_test_data() -> None:
    """Вызывает функцию drop_tables() для очистки данных"""
    conn: Optional[psycopg2.extensions.connection] = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "test_db"),
            user=os.getenv("DB_POSTGRES_ADMIN", "test_user"),
            password=os.getenv("DB_POSTGRES_PASSWORD", "test_password")
        )

        with conn.cursor() as cursor:
            cursor.execute("CALL drop_tables();")

        conn.commit()

    except Exception as e:
        print(f"Ошибка при очистке базы данных: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


@pytest.fixture(autouse=True)
def cleanup_db():
    clear_test_data()
    yield
    clear_test_data()


@pytest.fixture
def test_graph(client):
    graph_data = {
        "nodes": [{"name": "A"}, {"name": "B"}],
        "edges": [{"source": "A", "target": "B"}]
    }
    response = client.post("/api/graph/", json=graph_data)
    yield response.json()["id"]
    client.delete(f"/api/graph/{response.json()['id']}")
