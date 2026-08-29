import uuid

from app.core.config import settings


def _unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:10]}@example.com"


async def _auth_headers(client, org_name="KB Test Org"):
    payload = {
        "email": _unique_email(),
        "password": "supersecret1",
        "full_name": "Katherine Johnson",
        "org_name": org_name,
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _create_kb(client, headers, name="Product Docs"):
    response = await client.post("/api/v1/knowledge-bases", json={"name": name}, headers=headers)
    assert response.status_code == 201
    return response.json()


async def test_create_and_list_knowledge_bases(client):
    headers = await _auth_headers(client)

    kb = await _create_kb(client, headers)
    assert kb["name"] == "Product Docs"
    assert kb["doc_count"] == 0
    assert kb["chunk_count"] == 0

    response = await client.get("/api/v1/knowledge-bases", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == kb["id"]


async def test_get_knowledge_base_not_found(client):
    headers = await _auth_headers(client)

    response = await client.get(f"/api/v1/knowledge-bases/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 404


async def test_knowledge_base_is_org_scoped(client):
    headers_a = await _auth_headers(client, org_name="KB Org A")
    headers_b = await _auth_headers(client, org_name="KB Org B")

    kb = await _create_kb(client, headers_a)

    response = await client.get(f"/api/v1/knowledge-bases/{kb['id']}", headers=headers_b)
    assert response.status_code == 404


async def test_upload_document_success(client):
    headers = await _auth_headers(client)
    kb = await _create_kb(client, headers)

    files = {"file": ("handbook.txt", b"Hello knowledge base!", "text/plain")}
    response = await client.post(
        f"/api/v1/knowledge-bases/{kb['id']}/documents", headers=headers, files=files
    )

    assert response.status_code == 202
    body = response.json()
    assert body["filename"] == "handbook.txt"
    assert body["status"] == "pending"

    kb_response = await client.get(f"/api/v1/knowledge-bases/{kb['id']}", headers=headers)
    assert kb_response.json()["doc_count"] == 1


async def test_upload_document_rejects_unsupported_extension(client):
    headers = await _auth_headers(client)
    kb = await _create_kb(client, headers)

    files = {"file": ("malware.exe", b"binary-content", "application/octet-stream")}
    response = await client.post(
        f"/api/v1/knowledge-bases/{kb['id']}/documents", headers=headers, files=files
    )

    assert response.status_code == 400


async def test_upload_document_rejects_oversized_file(client, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_mb", 0)

    headers = await _auth_headers(client)
    kb = await _create_kb(client, headers)

    files = {"file": ("notes.txt", b"just a little too big", "text/plain")}
    response = await client.post(
        f"/api/v1/knowledge-bases/{kb['id']}/documents", headers=headers, files=files
    )

    assert response.status_code == 400


async def test_upload_document_for_missing_kb_returns_404(client):
    headers = await _auth_headers(client)

    files = {"file": ("notes.txt", b"content", "text/plain")}
    response = await client.post(
        f"/api/v1/knowledge-bases/{uuid.uuid4()}/documents", headers=headers, files=files
    )

    assert response.status_code == 404


async def test_list_get_and_delete_document(client):
    headers = await _auth_headers(client)
    kb = await _create_kb(client, headers)

    files = {"file": ("readme.md", b"# Title\nSome content.", "text/markdown")}
    upload_response = await client.post(
        f"/api/v1/knowledge-bases/{kb['id']}/documents", headers=headers, files=files
    )
    document_id = upload_response.json()["id"]

    list_response = await client.get(
        f"/api/v1/knowledge-bases/{kb['id']}/documents", headers=headers
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = await client.get(f"/api/v1/documents/{document_id}", headers=headers)
    assert detail_response.status_code == 200
    assert set(detail_response.json().keys()) == {
        "id",
        "filename",
        "status",
        "chunk_count",
        "error_message",
    }

    delete_response = await client.delete(f"/api/v1/documents/{document_id}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = await client.get(f"/api/v1/documents/{document_id}", headers=headers)
    assert missing_response.status_code == 404

    kb_response = await client.get(f"/api/v1/knowledge-bases/{kb['id']}", headers=headers)
    assert kb_response.json()["doc_count"] == 0


async def test_deleting_knowledge_base_removes_documents(client):
    headers = await _auth_headers(client)
    kb = await _create_kb(client, headers)

    files = {"file": ("readme.md", b"# Title\nSome content.", "text/markdown")}
    upload_response = await client.post(
        f"/api/v1/knowledge-bases/{kb['id']}/documents", headers=headers, files=files
    )
    document_id = upload_response.json()["id"]

    delete_kb_response = await client.delete(f"/api/v1/knowledge-bases/{kb['id']}", headers=headers)
    assert delete_kb_response.status_code == 204

    missing_kb_response = await client.get(f"/api/v1/knowledge-bases/{kb['id']}", headers=headers)
    assert missing_kb_response.status_code == 404

    missing_document_response = await client.get(
        f"/api/v1/documents/{document_id}", headers=headers
    )
    assert missing_document_response.status_code == 404
