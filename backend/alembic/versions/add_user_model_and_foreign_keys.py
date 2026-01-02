"""Add user model and user_id foreign keys

Revision ID: add_user_auth
Revises: e7d39a09f26f
Create Date: 2026-01-02 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_auth'
down_revision = '6fb41cc6bf7d'  # This should be the latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('supertokens_user_id', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_supertokens_user_id'), 'users', ['supertokens_user_id'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Add user_id to orders table (nullable first, then we'll make it NOT NULL)
    op.add_column('orders', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)
    
    # Add user_id to products table (nullable first)
    op.add_column('products', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_products_user_id'), 'products', ['user_id'], unique=False)
    
    # Add user_id to oauth_tokens table (nullable first)
    op.add_column('oauth_tokens', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_oauth_tokens_user_id'), 'oauth_tokens', ['user_id'], unique=False)
    
    # Remove unique constraint from orders.external_id (since it's now per-user)
    op.drop_index('ix_orders_external_id', table_name='orders')
    op.create_index(op.f('ix_orders_external_id'), 'orders', ['external_id'], unique=False)
    
    # Remove unique constraint from products.sku (since it's now per-user)
    op.drop_index('ix_products_sku', table_name='products', if_exists=True)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=False)
    
    # Create foreign keys
    op.create_foreign_key('fk_orders_user_id', 'orders', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_products_user_id', 'products', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_oauth_tokens_user_id', 'oauth_tokens', 'users', ['user_id'], ['id'])
    
    # Make user_id NOT NULL (only if tables are empty, otherwise you'll need to populate first)
    # If you have existing data, comment out these lines and populate user_id first
    op.alter_column('orders', 'user_id', nullable=False)
    op.alter_column('products', 'user_id', nullable=False)
    op.alter_column('oauth_tokens', 'user_id', nullable=False)


def downgrade() -> None:
    # Remove foreign keys and columns
    op.drop_constraint('fk_oauth_tokens_user_id', 'oauth_tokens', type_='foreignkey')
    op.drop_index(op.f('ix_oauth_tokens_user_id'), table_name='oauth_tokens')
    op.drop_column('oauth_tokens', 'user_id')
    
    op.drop_constraint('fk_products_user_id', 'products', type_='foreignkey')
    op.drop_index(op.f('ix_products_user_id'), table_name='products')
    op.drop_column('products', 'user_id')
    
    op.drop_constraint('fk_orders_user_id', 'orders', type_='foreignkey')
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_column('orders', 'user_id')
    
    # Restore unique constraints
    op.drop_index(op.f('ix_orders_external_id'), table_name='orders')
    op.create_index('ix_orders_external_id', 'orders', ['external_id'], unique=True)
    
    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)
    
    # Drop users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_supertokens_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

