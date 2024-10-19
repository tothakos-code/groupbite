"""initial_migration

Revision ID: f1b1f2654a93
Revises:
Create Date: 2024-10-19 13:40:07.478039

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f1b1f2654a93'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('setting',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('username', sa.Text(), nullable=False),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('theme', sa.Enum('LIGHT', 'DARK', name='theme'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_unique_constraint(None, 'user', ['id'])
    op.create_table('vendor',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('type', sa.Enum('PLUGIN', 'BASIC', name='vendortype'), nullable=False),
    sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_unique_constraint(None, 'vendor', ['id'])
    op.create_table('menu',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('vendor_id', sa.Uuid(), nullable=False),
    sa.Column('freq_id', sa.Enum('FIX', 'DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY', name='frequency'), nullable=False),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('vendor_id', sa.Uuid(), nullable=False),
    sa.Column('state_id', sa.Enum('COLLECT', 'ORDER', 'CLOSED', name='orderstate'), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('date_of_order', sa.Date(), nullable=False),
    sa.Column('order_time', sa.DateTime(), nullable=True),
    sa.Column('order_fee', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('menu_item',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('menu_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['menu_id'], ['menu.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('size',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('menu_item_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('link', sa.String(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('index', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['menu_item_id'], ['menu_item.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id', 'menu_item_id', name='uq_size_item')
    )
    op.create_table('user_basket',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('menu_item_id', sa.Integer(), nullable=False),
    sa.Column('size_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['menu_item_id'], ['menu_item.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['size_id', 'menu_item_id'], ['size.id', 'size.menu_item_id'], name='fk_size_item'),
    sa.ForeignKeyConstraint(['size_id'], ['size.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'menu_item_id', 'size_id', 'order_id')
    )
    op.execute(
        """INSERT INTO setting (key, value, category) VALUES
        ('smtp_address', '', 'smtp'),
        ('smtp_port', '', 'smtp'),
        ('smtp_user', '', 'smtp'),
        ('smtp_password', '', 'smtp'),
        ('smtp_sender_email', '', 'smtp'),
        ('app_title', 'Groupbite', 'application')
        """
    )


def downgrade():
    op.drop_table('user_basket')
    op.drop_table('size')
    op.drop_table('menu_item')
    op.drop_table('order')
    op.drop_table('menu')
    op.drop_table('vendor')
    op.drop_table('user')
    op.drop_table('setting')
