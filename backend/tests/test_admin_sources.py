import pytest

pytest.importorskip("fastapi")
def test_list_sources_empty(client):
    response = client.get("/api/admin/sources")
    assert response.status_code == 200
    assert response.json()["sources"] == []


def test_create_and_toggle_source(client, db_session):
    payload = {
        "name": "Test Feed",
        "base_url": "https://example.com",
        "language": "en",
        "priority": 5,
    }

    create_response = client.post("/api/admin/sources", json=payload)
    assert create_response.status_code == 200
    source_id = create_response.json()["source"]["id"]

    list_response = client.get("/api/admin/sources")
    assert list_response.status_code == 200
    assert list_response.json()["sources"][0]["name"] == "Test Feed"

    toggle_response = client.post(f"/api/admin/sources/{source_id}/toggle", params={"enabled": False})
    assert toggle_response.status_code == 200
    assert toggle_response.json()["source"]["enabled"] is False


def test_ingestion_history_defaults(client, db_session):
    client.post(
        "/api/admin/sources",
        json={
            "name": "History Source",
            "base_url": "https://history.example",
        },
    )

    response = client.get("/api/admin/sources")
    source_id = response.json()["sources"][0]["id"]

    history_response = client.get(f"/api/admin/sources/{source_id}/ingestion")
    assert history_response.status_code == 200
    assert history_response.json()["history"] == []
