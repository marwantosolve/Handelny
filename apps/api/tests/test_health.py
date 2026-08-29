async def test_health_check_returns_status(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "checks" in body
    assert set(body["checks"].keys()) == {"database", "qdrant"}
