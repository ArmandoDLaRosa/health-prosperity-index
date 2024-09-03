"""Create initial tables

Revision ID: e4cec76e2ebc
Revises: 
Create Date: 2024-09-02 18:18:28.076067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e4cec76e2ebc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE TABLE index_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            year INT UNIQUE,
            index_value FLOAT,
            created_at DATETIME,
            updated_at DATETIME
        );
    """)

    op.execute("""
        CREATE TABLE cron_job_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            run_time DATETIME,
            status VARCHAR(255),
            message TEXT
        );
    """)
    
    op.execute("""
        CREATE TABLE index_components (
            id INT AUTO_INCREMENT PRIMARY KEY,
            year INT UNIQUE,
            population BIGINT,
            household_income BIGINT,
            number_of_finishers INT,
            number_covered BIGINT,
            household_ownership BIGINT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS cron_job_logs;")
    op.execute("DROP TABLE IF EXISTS index_table;")