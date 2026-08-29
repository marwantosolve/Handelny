import uuid


def _unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:10]}@example.com"


async def _register(client, *, email=None, password="supersecret1", full_name="Ada Lovelace", org_name="Acme Inc"):
    payload = {
        "email": email or _unique_email(),
        "password": password,
        "full_name": full_name,
        "org_name": org_name,
    }
    return await client.post("/api/v1/auth/register", json=payload)


async def test_register_creates_user_and_organization(client):
    response = await _register(client, org_name="Acme Widgets")

    assert response.status_code == 201
    body = response.json()

    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]

    assert set(body["user"].keys()) == {"id", "email", "full_name"}
    assert body["user"]["full_name"] == "Ada Lovelace"

    assert set(body["organization"].keys()) == {"id", "name", "slug"}
    assert body["organization"]["name"] == "Acme Widgets"
    assert body["organization"]["slug"] == "acme-widgets"


async def test_register_dedupes_organization_slug(client):
    first = await _register(client, org_name="Duplicate Co")
    second = await _register(client, org_name="Duplicate Co")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["organization"]["slug"] == "duplicate-co"
    assert second.json()["organization"]["slug"] == "duplicate-co-2"


async def test_register_duplicate_email_conflicts(client):
    email = _unique_email()

    first = await _register(client, email=email)
    assert first.status_code == 201

    second = await _register(client, email=email, org_name="Another Org")
    assert second.status_code == 409
    assert second.json()["error"]["type"] == "ConflictError"


async def test_login_success(client):
    email = _unique_email()
    password = "supersecret1"
    register_response = await _register(client, email=email, password=password)
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )

    assert login_response.status_code == 200
    body = login_response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]


async def test_login_invalid_password(client):
    email = _unique_email()
    await _register(client, email=email, password="supersecret1")

    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "wrong-password"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid email or password"


async def test_login_unknown_email(client):
    response = await client.post(
        "/api/v1/auth/login", json={"email": _unique_email(), "password": "whatever1"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid email or password"


async def test_me_requires_authentication(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_returns_current_principal(client):
    register_response = await _register(client, org_name="Me Endpoint Org")
    access_token = register_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "owner"
    assert body["organization"]["name"] == "Me Endpoint Org"
    assert body["user"]["email"] == register_response.json()["user"]["email"]
