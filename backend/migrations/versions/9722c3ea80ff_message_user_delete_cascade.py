"""message user delete cascade

Revision ID: 9722c3ea80ff
Revises: 7ee4dafd63e2
Create Date: 2024-10-22 00:49:14.003842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9722c3ea80ff'
down_revision: Union[str, None] = '7ee4dafd63e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_messages_user_to_id_users', 'messages', type_='foreignkey')
    op.drop_constraint('fk_messages_user_from_id_users', 'messages', type_='foreignkey')
    op.create_foreign_key(op.f('fk_messages_user_to_id_users'), 'messages', 'users', ['user_to_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_messages_user_from_id_users'), 'messages', 'users', ['user_from_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_messages_user_from_id_users'), 'messages', type_='foreignkey')
    op.drop_constraint(op.f('fk_messages_user_to_id_users'), 'messages', type_='foreignkey')
    op.create_foreign_key('fk_messages_user_from_id_users', 'messages', 'users', ['user_from_id'], ['id'])
    op.create_foreign_key('fk_messages_user_to_id_users', 'messages', 'users', ['user_to_id'], ['id'])
    # ### end Alembic commands ###
