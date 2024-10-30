"""user created_at

Revision ID: f18bda8d1da3
Revises: 889b51cb531a
Create Date: 2024-10-30 19:32:59.138908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f18bda8d1da3'
down_revision: Union[str, None] = '889b51cb531a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_messages_uuid_id', table_name='messages')
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=False,
                                     server_default=sa.text('NOW()')))  # <-- added to populate existing rows
    op.drop_index('ix_users_uuid_id', table_name='users')
    op.drop_constraint('uq_users_id', 'users', type_='unique')
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.create_unique_constraint('uq_users_id', 'users', ['id'])
    op.create_index('ix_users_uuid_id', 'users', ['id'], unique=True)
    op.drop_column('users', 'created_at')
    op.create_index('ix_messages_uuid_id', 'messages', ['id'], unique=True)
    # ### end Alembic commands ###
