"""auto_migration

Revision ID: c02e12487d73
Revises: e0175f82b284
Create Date: 2026-04-25 15:08:25.009292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c02e12487d73'
down_revision = 'e0175f82b284'
branch_labels = None
depends_on = None


def upgrade():
    # Add as nullable first so backfill can run before enforcing NOT NULL
    op.add_column('order', sa.Column('open_from', sa.Date(), nullable=True))
    op.add_column('order', sa.Column('open_until', sa.Date(), nullable=True))

    op.execute('UPDATE "order" SET open_from = date_of_order')

    op.alter_column('order', 'open_from', nullable=False)

    op.drop_index('idx_order_date_desc', table_name='order')
    op.create_index('idx_order_date_desc', 'order', [sa.text('open_from DESC')], unique=False)
    op.drop_index('idx_order_vendor_date', table_name='order')
    op.create_index('idx_order_vendor_date', 'order', ['vendor_id', sa.text('open_from DESC')], unique=False)

    op.drop_column('order', 'date_of_order')


def downgrade():
    op.add_column('order', sa.Column('date_of_order', sa.DATE(), autoincrement=False, nullable=True))

    op.execute('UPDATE "order" SET date_of_order = open_from')

    op.alter_column('order', 'date_of_order', nullable=False)

    op.drop_index('idx_order_vendor_date', table_name='order')
    op.create_index('idx_order_vendor_date', 'order', ['vendor_id', sa.text('date_of_order DESC')], unique=False)
    op.drop_index('idx_order_date_desc', table_name='order')
    op.create_index('idx_order_date_desc', 'order', [sa.text('date_of_order DESC')], unique=False)

    op.drop_column('order', 'open_until')
    op.drop_column('order', 'open_from')
