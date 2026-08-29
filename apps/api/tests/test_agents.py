import uuid


def _unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:10]}@example.com"


async def _auth_headers(client, org_name="Agents Test Org"):
    payload = {
        "email": _unique_email(),
        "password": "supersecret1",
        "full_name": "Grace Hopper",
        "org_name": org_name,
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_agent_uses_defaults(client):
    headers = await _auth_headers(client)

    response = await client.post(
        "/api/v1/agents", json={"name": "Support Bot"}, headers=headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Support Bot"
    assert body["is_active"] is True
    assert body["language"] == "auto"
    assert body["kb_id"] is None
    assert "system_prompt" in body and body["system_prompt"]


async def test_create_agent_with_overrides(client):
    headers = await _auth_headers(client)

    response = await client.post(
        "/api/v1/agents",
        json={
            "name": "French Bot",
            "system_prompt": "Reponds en francais uniquement.",
            "welcome_message": "Bonjour!",
            "fallback_message": "Je ne sais pas.",
            "language": "fr",
        },
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["language"] == "fr"
    assert body["welcome_message"] == "Bonjour!"


async def test_list_agents_is_org_scoped(client):
    headers_a = await _auth_headers(client, org_name="Org A")
    headers_b = await _auth_headers(client, org_name="Org B")

    await client.post("/api/v1/agents", json={"name": "Org A Bot"}, headers=headers_a)

    response_a = await client.get("/api/v1/agents", headers=headers_a)
    response_b = await client.get("/api/v1/agents", headers=headers_b)

    assert response_a.status_code == 200
    assert response_b.status_code == 200
    assert len(response_a.json()) == 1
    assert response_a.json()[0]["name"] == "Org A Bot"
    assert response_b.json() == []


async def test_get_update_delete_agent_lifecycle(client):
    headers = await _auth_headers(client)

    create_response = await client.post(
        "/api/v1/agents", json={"name": "Lifecycle Bot"}, headers=headers
    )
    agent_id = create_response.json()["id"]

    get_response = await client.get(f"/api/v1/agents/{agent_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Lifecycle Bot"

    patch_response = await client.patch(
        f"/api/v1/agents/{agent_id}", json={"name": "Renamed Bot"}, headers=headers
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == "Renamed Bot"

    delete_response = await client.delete(f"/api/v1/agents/{agent_id}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = await client.get(f"/api/v1/agents/{agent_id}", headers=headers)
    assert missing_response.status_code == 404


async def test_agent_not_found_across_orgs(client):
    headers_a = await _auth_headers(client, org_name="Isolated Org A")
    headers_b = await _auth_headers(client, org_name="Isolated Org B")

    create_response = await client.post(
        "/api/v1/agents", json={"name": "Private Bot"}, headers=headers_a
    )
    agent_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/agents/{agent_id}", headers=headers_b)
    assert response.status_code == 404


async def test_create_agent_with_unknown_kb_id_returns_404(client):
    headers = await _auth_headers(client)

    response = await client.post(
        "/api/v1/agents",
        json={"name": "KB Bot", "kb_id": str(uuid.uuid4())},
        headers=headers,
    )

    assert response.status_code == 404
