"""Add continuous aggregate view for X-minute averages

Revision ID: b698a9acf15a
Revises: 55ec7006783b

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "b698a9acf15a"
down_revision: Union[str, None] = "55ec7006783b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Access the connection
    conn = op.get_bind()

    # Create the continuous aggregate materialized view without data
    conn.execute(
        text(
            """
        CREATE MATERIALIZED VIEW avg_temperature_time_interval
        WITH (timescaledb.continuous) AS
        SELECT time_bucket('2 minutes', timestamp) AS bucket,
               building_id,
               room_id,
               AVG(temperature) AS avg_temp
        FROM temperatures
        GROUP BY bucket, building_id, room_id
        WITH NO DATA;
    """
        )
    )

    # Add a policy to refresh the view periodically
    conn.execute(
        text(
            """
    SELECT add_continuous_aggregate_policy('avg_temperature_time_interval',
        start_offset => INTERVAL '1 hour',
        end_offset => INTERVAL '10 seconds',
        schedule_interval => INTERVAL '5 seconds');
    """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("DROP MATERIALIZED VIEW IF EXISTS avg_temperature_time_interval;")
    )
