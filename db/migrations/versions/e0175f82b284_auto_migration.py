"""auto_migration

Revision ID: e0175f82b284
Revises: 381441160229
Create Date: 2026-04-23 18:44:19.744456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0175f82b284'
down_revision = '381441160229'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'category',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vendor_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vendor_id', 'name', name='uq_category_vendor_name'),
    )

    # Backfill: insert one Category row per distinct (vendor_id, category_name) pair.
    # Empty/null category strings are treated as "egyéb" (matches the runtime fallback).
    op.execute("""
        INSERT INTO category (vendor_id, name)
        SELECT DISTINCT m.vendor_id, COALESCE(NULLIF(TRIM(mi.category), ''), 'egyéb')
        FROM menu_item mi
        JOIN menu m ON m.id = mi.menu_id
    """)

    # Add category_id as nullable first so the column can be created on non-empty tables.
    op.add_column('menu_item', sa.Column('category_id', sa.Integer(), nullable=True))

    # Backfill category_id by matching the old category string to the new category rows.
    op.execute("""
        UPDATE menu_item mi
        SET category_id = c.id
        FROM menu m, category c
        WHERE m.id = mi.menu_id
          AND c.vendor_id = m.vendor_id
          AND c.name = COALESCE(NULLIF(TRIM(mi.category), ''), 'egyéb')
    """)

    op.alter_column('menu_item', 'category_id', nullable=False)
    op.create_foreign_key('fk_menu_item_category', 'menu_item', 'category', ['category_id'], ['id'])
    op.drop_column('menu_item', 'category')


def downgrade():
    op.add_column('menu_item', sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=True))

    # Restore category string from the category table.
    op.execute("""
        UPDATE menu_item mi
        SET category = c.name
        FROM category c
        WHERE c.id = mi.category_id
    """)

    op.alter_column('menu_item', 'category', nullable=False)
    op.drop_constraint('fk_menu_item_category', 'menu_item', type_='foreignkey')
    op.drop_column('menu_item', 'category_id')
    op.drop_table('category')
