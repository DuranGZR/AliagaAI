"""change_vector_index_to_hnsw

Revision ID: 2fa716425f3a
Revises: 058411e7a86e
Create Date: 2026-06-04 20:33:04.994241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fa716425f3a'
down_revision: Union[str, Sequence[str], None] = '058411e7a86e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old ivfflat index
    op.execute("DROP INDEX IF EXISTS idx_chunks_embedding")
    # Create the new HNSW index with vector_cosine_ops
    op.execute(
        "CREATE INDEX idx_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the HNSW index
    op.execute("DROP INDEX IF EXISTS idx_chunks_embedding")
    # Recreate the old ivfflat index
    op.execute(
        "CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops)"
    )
