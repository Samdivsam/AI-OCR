import pytest

from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_financial_endpoints(client, sample_pdf_bytes) -> None:
    auth = await register_and_login(client, email="finance@example.com")
    token = auth["access_token"]

    upload = await client.post(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("bank.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 201
    assert upload.json()["document_type"] == "BANK_STATEMENT"

    summary = await client.get(
        "/api/v1/financial/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert summary.status_code == 200
    assert summary.json()["transaction_count"] == 2

    transactions = await client.get(
        "/api/v1/financial/transactions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert transactions.status_code == 200
    assert len(transactions.json()) == 2

    monthly = await client.get(
        "/api/v1/financial/monthly-summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert monthly.status_code == 200
    assert monthly.json()["items"][0]["month"] == "2024-01"

