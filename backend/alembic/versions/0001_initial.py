"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"], unique=False)
    op.create_index("ix_documents_document_type", "documents", ["document_type"], unique=False)
    op.create_index("ix_documents_created_at", "documents", ["created_at"], unique=False)

    op.create_table(
        "document_extractions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raw_ocr_text", sa.Text(), nullable=True),
        sa.Column("extracted_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("extraction_version", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("document_id"),
    )
    op.create_index("ix_document_extractions_document_id", "document_extractions", ["document_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_document_extractions_document_id", table_name="document_extractions")
    op.drop_table("document_extractions")
    op.drop_index("ix_documents_created_at", table_name="documents")
    op.drop_index("ix_documents_document_type", table_name="documents")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

