"""Create temperatures table

Revision ID: 55ec7006783b
Revises:

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55ec7006783b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create the table with a composite primary key
    op.create_table(
        'temperatures',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('building_id', sa.String(), nullable=False),
        sa.Column('room_id', sa.String(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', 'timestamp')
    )

    # Add composite index for optimization
    op.create_index(
        "idx_building_room_timestamp",
        "temperatures",
        ["building_id", "room_id", "timestamp"],
    )

    # Enable TimescaleDB and convert to hypertable
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
        SELECT create_hypertable('temperatures', 'timestamp');
    """)

def downgrade() -> None:
    # Drop the table and associated indexes
    op.drop_index("idx_building_room_timestamp", table_name="temperatures")
    op.drop_table("temperatures")