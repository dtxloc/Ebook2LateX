"""Tao cac bang ban dau cho Ebook2LateX

Revision ID: 85f853a58692
Revises: 
Create Date: 2026-05-03 21:10:27.250950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '85f853a58692'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_target_tables() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("username_email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("username_email", name="uq_users_username_email"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("file_path_url", sa.Text(), nullable=False),
        sa.Column("upload_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "formula_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("raw_image_path", sa.Text(), nullable=True),
        sa.Column("latex_content", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "logs",
        sa.Column("log_id", sa.UUID(), nullable=False),
        sa.Column("formula_id", sa.UUID(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("confidence_score", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("error_type", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("environment_info", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["formula_id"], ["formula_entries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("log_id"),
    )


def _create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_formula_entries_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_formula_entries_set_updated_at
        BEFORE UPDATE ON formula_entries
        FOR EACH ROW
        EXECUTE FUNCTION set_formula_entries_updated_at();
        """
    )


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Migrate from legacy camel/flat naming if those tables exist.
    legacy_tables = {"users", "documents", "formulaentries", "logs"}
    if legacy_tables.issubset(tables):
        op.create_table(
            "users_new",
            sa.Column("user_id", sa.UUID(), nullable=False),
            sa.Column("username_email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.Text(), nullable=False),
            sa.Column("full_name", sa.String(length=100), nullable=True),
            sa.Column("role", sa.String(length=20), nullable=True),
            sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.PrimaryKeyConstraint("user_id"),
            sa.UniqueConstraint("username_email", name="uq_users_new_username_email"),
        )
        op.execute(
            """
            CREATE TEMP TABLE tmp_user_map AS
            SELECT userid AS old_userid, gen_random_uuid() AS new_user_id
            FROM users;
            """
        )
        op.execute(
            """
            INSERT INTO users_new (user_id, username_email, password_hash, full_name, role, last_login, is_active, created_at)
            SELECT
                m.new_user_id,
                COALESCE(NULLIF(TRIM(u.email), ''), 'user_' || u.userid || '@local.invalid') AS username_email,
                COALESCE(u.passwordhash, ''),
                u.fullname,
                COALESCE(u.role, 'Editor'),
                u.lastlogin,
                COALESCE(u.isactive, TRUE),
                NOW()
            FROM users u
            JOIN tmp_user_map m ON m.old_userid = u.userid;
            """
        )

        op.create_table(
            "documents_new",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("user_id", sa.UUID(), nullable=True),
            sa.Column("file_name", sa.Text(), nullable=False),
            sa.Column("file_path_url", sa.Text(), nullable=False),
            sa.Column("upload_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users_new.user_id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.execute(
            """
            CREATE TEMP TABLE tmp_document_map AS
            SELECT id AS old_document_id, gen_random_uuid() AS new_document_id
            FROM documents;
            """
        )
        op.execute(
            """
            INSERT INTO documents_new (id, user_id, file_name, file_path_url, upload_date, status)
            SELECT
                dm.new_document_id,
                um.new_user_id,
                d.filename,
                d.filepath,
                d.uploaddate,
                COALESCE(d.status, 'Pending')
            FROM documents d
            JOIN tmp_document_map dm ON dm.old_document_id = d.id
            LEFT JOIN tmp_user_map um ON um.old_userid = d.userid;
            """
        )

        op.create_table(
            "formula_entries_new",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("document_id", sa.UUID(), nullable=False),
            sa.Column("raw_image_path", sa.Text(), nullable=True),
            sa.Column("latex_content", sa.Text(), nullable=True),
            sa.Column("order_index", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(["document_id"], ["documents_new.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.execute(
            """
            CREATE TEMP TABLE tmp_formula_map AS
            SELECT id AS old_formula_id, gen_random_uuid() AS new_formula_id
            FROM formulaentries;
            """
        )
        op.execute(
            """
            INSERT INTO formula_entries_new (id, document_id, raw_image_path, latex_content, order_index, created_at, updated_at)
            SELECT
                fm.new_formula_id,
                dm.new_document_id,
                f.imagepath,
                f.latexcontent,
                COALESCE(f.orderindex, 0),
                COALESCE(f.createdat, NOW()),
                COALESCE(f.updatedat, NOW())
            FROM formulaentries f
            JOIN tmp_formula_map fm ON fm.old_formula_id = f.id
            JOIN tmp_document_map dm ON dm.old_document_id = f.documentid;
            """
        )

        op.create_table(
            "logs_new",
            sa.Column("log_id", sa.UUID(), nullable=False),
            sa.Column("formula_id", sa.UUID(), nullable=True),
            sa.Column("processing_time_ms", sa.Integer(), nullable=True),
            sa.Column("confidence_score", sa.Numeric(precision=3, scale=2), nullable=True),
            sa.Column("error_type", sa.String(length=100), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("environment_info", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.ForeignKeyConstraint(["formula_id"], ["formula_entries_new.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("log_id"),
        )
        op.execute(
            """
            INSERT INTO logs_new (log_id, formula_id, processing_time_ms, confidence_score, error_type, error_message, timestamp, environment_info)
            SELECT
                gen_random_uuid(),
                fm.new_formula_id,
                CASE
                    WHEN l.processingtime IS NULL THEN NULL
                    ELSE ROUND(l.processingtime)::INTEGER
                END,
                CASE
                    WHEN l.confidencescore IS NULL THEN NULL
                    WHEN l.confidencescore >= 0 AND l.confidencescore <= 9.99 THEN ROUND(l.confidencescore::numeric, 2)::numeric(3, 2)
                    ELSE NULL
                END,
                l.errortype,
                l.errormessage,
                l.timestamp,
                CASE
                    WHEN l.environmentinfo IS NULL OR TRIM(l.environmentinfo) = '' THEN NULL
                    ELSE jsonb_build_object('raw_text', l.environmentinfo)
                END
            FROM logs l
            LEFT JOIN tmp_formula_map fm ON fm.old_formula_id = l.formulaid;
            """
        )

        op.drop_table("logs")
        op.drop_table("formulaentries")
        op.drop_table("documents")
        op.drop_table("users")

        op.rename_table("users_new", "users")
        op.rename_table("documents_new", "documents")
        op.rename_table("formula_entries_new", "formula_entries")
        op.rename_table("logs_new", "logs")
    else:
        _create_target_tables()

    _create_updated_at_trigger()


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_formula_entries_set_updated_at ON formula_entries")
    op.execute("DROP FUNCTION IF EXISTS set_formula_entries_updated_at")

    op.drop_table("logs")
    op.drop_table("formula_entries")
    op.drop_table("documents")
    op.drop_table("users")
