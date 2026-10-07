import pytest

from tests.conftest import register_and_login


async def _upload(client, token: str, name: str, content: bytes, mime: str):
    return await client.post(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (name, content, mime)},
    )


async def _upload_with_type(client, token: str, name: str, content: bytes, mime: str, document_type: str):
    return await client.post(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {token}"},
        data={"document_type": document_type},
        files={"file": (name, content, mime)},
    )


@pytest.mark.asyncio
async def test_user_can_access_own_document(client, sample_pdf_bytes) -> None:
    auth = await register_and_login(client)
    response = await _upload(client, auth["access_token"], "id-card.pdf", sample_pdf_bytes, "application/pdf")
    assert response.status_code == 201
    document_id = response.json()["document_id"]

    details = await client.get(
        f"/api/v1/documents/{document_id}",
        headers={"Authorization": f"Bearer {auth['access_token']}"},
    )
    assert details.status_code == 200
    assert details.json()["id"] == document_id


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_document(client, sample_pdf_bytes) -> None:
    owner = await register_and_login(client, email="owner@example.com")
    other = await register_and_login(client, email="other@example.com")
    upload = await _upload(client, owner["access_token"], "id-card.pdf", sample_pdf_bytes, "application/pdf")
    document_id = upload.json()["document_id"]

    details = await client.get(
        f"/api/v1/documents/{document_id}",
        headers={"Authorization": f"Bearer {other['access_token']}"},
    )
    assert details.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_delete_another_users_document(client, sample_pdf_bytes) -> None:
    owner = await register_and_login(client, email="delete-owner@example.com")
    other = await register_and_login(client, email="delete-other@example.com")
    upload = await _upload(client, owner["access_token"], "id-card.pdf", sample_pdf_bytes, "application/pdf")
    document_id = upload.json()["document_id"]

    deletion = await client.delete(
        f"/api/v1/documents/{document_id}",
        headers={"Authorization": f"Bearer {other['access_token']}"},
    )
    assert deletion.status_code == 404


@pytest.mark.asyncio
async def test_valid_pdf_upload(client, sample_pdf_bytes) -> None:
    auth = await register_and_login(client)
    response = await _upload(client, auth["access_token"], "bank.pdf", sample_pdf_bytes, "application/pdf")
    assert response.status_code == 201
    assert response.json()["status"] == "COMPLETED"
    assert response.json()["extraction"]["ocr_text_preview"]


@pytest.mark.asyncio
async def test_valid_jpg_upload(client, sample_jpg_bytes) -> None:
    auth = await register_and_login(client)
    response = await _upload(client, auth["access_token"], "passport.jpg", sample_jpg_bytes, "image/jpeg")
    assert response.status_code == 201
    assert response.json()["document_type"] == "PASSPORT"


@pytest.mark.asyncio
async def test_valid_png_upload(client, sample_png_bytes) -> None:
    auth = await register_and_login(client)
    response = await _upload(client, auth["access_token"], "salary.png", sample_png_bytes, "image/png")
    assert response.status_code == 201
    assert response.json()["document_type"] == "SALARY_SLIP"


@pytest.mark.asyncio
async def test_invalid_file_type(client) -> None:
    auth = await register_and_login(client)
    response = await _upload(client, auth["access_token"], "bad.txt", b"text", "text/plain")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


@pytest.mark.asyncio
async def test_file_too_large(client) -> None:
    auth = await register_and_login(client)
    large_pdf = b"%PDF" + (b"a" * (2 * 1024 * 1024))
    response = await _upload(client, auth["access_token"], "large.pdf", large_pdf, "application/pdf")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"


@pytest.mark.asyncio
async def test_empty_file(client) -> None:
    auth = await register_and_login(client)
    response = await _upload(client, auth["access_token"], "empty.pdf", b"", "application/pdf")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_FILE"


@pytest.mark.asyncio
async def test_explicit_document_type_override(client, sample_pdf_bytes) -> None:
    auth = await register_and_login(client, email="override@example.com")
    response = await _upload_with_type(
        client,
        auth["access_token"],
        "id-card.pdf",
        sample_pdf_bytes,
        "application/pdf",
        "BANK_STATEMENT",
    )
    assert response.status_code == 201
    assert response.json()["document_type"] == "BANK_STATEMENT"


