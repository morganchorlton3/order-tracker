"""Add name field to user model

Revision ID: add_name_to_user
Revises: add_user_auth
Create Date: 2026-01-02 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_name_to_user'
down_revision = 'add_user_auth'  # Matches the revision from add_user_model_and_foreign_keys.py
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add name column to users table (nullable first, then we'll populate and make it non-null)
    op.add_column('users', sa.Column('name', sa.String(), nullable=True))
    
    # Populate existing users with their email as name
    op.execute("UPDATE users SET name = email WHERE name IS NULL")
    
    # Make name column non-nullable
    op.alter_column('users', 'name', nullable=False)


def downgrade() -> None:
    # Remove name column from users table
    op.drop_column('users', 'name')

