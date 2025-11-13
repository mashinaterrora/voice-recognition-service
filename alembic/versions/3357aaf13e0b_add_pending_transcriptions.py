from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3357aaf13e0b"
down_revision = "27cd419820af"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "pending_transcriptions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("file_id", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

def downgrade() -> None:
    op.drop_table("pending_transcriptions")