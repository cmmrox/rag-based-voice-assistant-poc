"""Add search_vector trigger

Revision ID: 86fff380304f
Revises: 41e0c796debc
Create Date: 2025-11-18 15:56:00.698005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86fff380304f'
down_revision: Union[str, Sequence[str], None] = '41e0c796debc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create trigger to automatically update search_vector
    # This trigger updates the search_vector column whenever title or content changes
    op.execute("""
        CREATE TRIGGER notes_search_vector_update
        BEFORE INSERT OR UPDATE ON notes
        FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content);
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the trigger
    op.execute("DROP TRIGGER IF EXISTS notes_search_vector_update ON notes;")
