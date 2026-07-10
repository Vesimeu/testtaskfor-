"""add cascade delete to alerts

Revision ID: 1a2b3c4d5e6f
Revises: 0d6439d2e79f
Create Date: 2026-07-10 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, Sequence[str], None] = '0d6439d2e79f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing foreign key
    op.drop_constraint('alerts_file_id_fkey', 'alerts', type_='foreignkey')
    # Add new foreign key with cascade delete
    op.create_foreign_key(
        'alerts_file_id_fkey',
        'alerts',
        'files',
        ['file_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('alerts_file_id_fkey', 'alerts', type_='foreignkey')
    op.create_foreign_key(
        'alerts_file_id_fkey',
        'alerts',
        'files',
        ['file_id'],
        ['id']
    )
