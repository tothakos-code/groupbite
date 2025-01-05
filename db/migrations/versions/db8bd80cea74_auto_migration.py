"""auto_migration

Revision ID: db8bd80cea74
Revises: b3fa6e8019f4
Create Date: 2025-01-04 21:56:37.422257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db8bd80cea74'
down_revision = 'b3fa6e8019f4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """INSERT INTO setting (key, value, category) VALUES
        ('smtp_security', 'plain', 'smtp')
        """
    )


def downgrade():
    op.execute(
        """DELETE FROM setting WHERE
        key = 'smtp_security' AND category = 'smtp'
        """
    )
