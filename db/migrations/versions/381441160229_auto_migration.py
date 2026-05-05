"""auto_migration

Revision ID: 381441160229
Revises: c7d8a55dd1f4
Create Date: 2026-04-22 23:28:18.551324

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '381441160229'
down_revision = 'c7d8a55dd1f4'
branch_labels = None
depends_on = None

menutype = sa.Enum('DAILY_MENU', 'FIXED_MENU', 'OWN_INVENTORY', name='menutype')
vendortype = postgresql.ENUM('PLUGIN', 'BASIC', name='vendortype', create_type=False)


def upgrade():
    # Add new columns — menu_type nullable first so existing rows don't violate NOT NULL
    menutype.create(op.get_bind(), checkfirst=True)
    op.add_column('vendor', sa.Column('menu_type', menutype, nullable=True))
    op.add_column('vendor', sa.Column('plugin_id', sa.String(), nullable=True))

    # Data migration: map old type values to new fields.
    # type='PLUGIN' rows: best-guess plugin_id = vendor name, daily menu behaviour.
    # type='BASIC' rows: fixed menu, no plugin.
    op.execute("UPDATE vendor SET menu_type = 'DAILY_MENU', plugin_id = name WHERE type = 'PLUGIN'")
    op.execute("UPDATE vendor SET menu_type = 'FIXED_MENU' WHERE type = 'BASIC'")

    op.alter_column('vendor', 'menu_type', nullable=False)
    op.drop_column('vendor', 'type')
    op.execute("DROP TYPE IF EXISTS vendortype")


def downgrade():
    vendortype.create(op.get_bind(), checkfirst=True)
    op.add_column('vendor', sa.Column('type', vendortype, nullable=True))

    op.execute("UPDATE vendor SET type = 'PLUGIN' WHERE menu_type = 'DAILY_MENU'")
    op.execute("UPDATE vendor SET type = 'BASIC' WHERE menu_type IN ('FIXED_MENU', 'OWN_INVENTORY')")

    op.alter_column('vendor', 'type', nullable=False)
    op.drop_column('vendor', 'plugin_id')
    op.drop_column('vendor', 'menu_type')
    op.execute("DROP TYPE IF EXISTS menutype")
