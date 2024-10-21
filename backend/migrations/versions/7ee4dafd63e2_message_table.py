"""message table

Revision ID: 7ee4dafd63e2
Revises: dd6529f6ef9f
Create Date: 2024-10-21 17:27:46.918191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ee4dafd63e2'
down_revision: Union[str, None] = 'dd6529f6ef9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_from_id', sa.Integer(), nullable=False),
    sa.Column('user_to_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_from_id'], ['users.id'], name=op.f('fk_messages_user_from_id_users')),
    sa.ForeignKeyConstraint(['user_to_id'], ['users.id'], name=op.f('fk_messages_user_to_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_messages'))
    )
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_messages_created_at'), table_name='messages')
    op.drop_table('messages')
    # ### end Alembic commands ###
