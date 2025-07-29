"""auto_migration

Revision ID: 50d5fa442754
Revises: 8e15a67c05e2
Create Date: 2025-07-29 21:45:51.294717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50d5fa442754'
down_revision = '8e15a67c05e2'
branch_labels = None
depends_on = None


def upgrade():
    with op.get_context().autocommit_block():
        # UserBasket table indexes
        op.create_index(
            'idx_userbasket_user_id',
            'user_basket',
            ['user_id'],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        op.create_index(
            'idx_userbasket_order_id',
            'user_basket',
            ['order_id'],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        op.create_index(
            'idx_userbasket_user_order',
            'user_basket',
            ['user_id', 'order_id'],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        # OrderItem table indexes
        op.create_index(
            'idx_orderitem_user_id',
            'order_item',
            ['user_id'],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        op.create_index(
            'idx_orderitem_order_id',
            'order_item',
            ['order_id'],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        op.create_index(
            'idx_orderitem_user_order',
            'order_item',
            ['user_id', 'order_id'],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        # Order table indexes
        op.create_index(
            'idx_order_date_desc',
            'order',
            [sa.text('date_of_order DESC')],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        op.create_index(
            'idx_order_vendor_id',
            'order',
            ['vendor_id'],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        op.create_index(
            'idx_order_state_id',
            'order',
            ['state_id'],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        op.create_index(
            'idx_order_vendor_date',
            'order',
            ['vendor_id', sa.text('date_of_order DESC')],
            postgresql_concurrently=True,
            if_not_exists=True
        )

        op.create_index(
            'idx_orderitem_item_name_gin',
            'order_item',
            ['item_name'],
            postgresql_using='gin',
            postgresql_ops={'item_name': 'gin_trgm_ops'},
            postgresql_concurrently=True,
            if_not_exists=True
        )

        op.create_index(
            'idx_orderitem_size_label_gin',
            'order_item',
            ['size_label'],
            postgresql_using='gin',
            postgresql_ops={'size_label': 'gin_trgm_ops'},
            postgresql_concurrently=True,
            if_not_exists=True
        )


def downgrade():
    # Drop indexes in reverse order
    op.drop_index('idx_orderitem_size_label_gin', table_name='order_item')
    op.drop_index('idx_orderitem_item_name_gin', table_name='order_item')
    op.drop_index('idx_order_vendor_date', table_name='order')
    op.drop_index('idx_order_state_id', table_name='order')
    op.drop_index('idx_order_vendor_id', table_name='order')
    op.drop_index('idx_order_date_desc', table_name='order')
    op.drop_index('idx_orderitem_user_order', table_name='order_item')
    op.drop_index('idx_orderitem_order_id', table_name='order_item')
    op.drop_index('idx_orderitem_user_id', table_name='order_item')
    op.drop_index('idx_userbasket_user_order', table_name='user_basket')
    op.drop_index('idx_userbasket_order_id', table_name='user_basket')
    op.drop_index('idx_userbasket_user_id', table_name='user_basket')
