"""user contacts col uuid, step2

Revision ID: a16e9c37fb11
Revises: a9c459dd00ed
Create Date: 2024-10-25 16:53:28.949561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a16e9c37fb11'
down_revision: Union[str, None] = 'a9c459dd00ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('user_uuid_id', sa.Uuid(), nullable=True))
    op.add_column('contacts', sa.Column('contact_uuid_id', sa.Uuid(), nullable=True))

    # --> update new columns with values from users table
    conn = op.get_bind()
    conn.execute(sa.text("""
        update contacts set
            user_uuid_id = (select uuid_id from users where id = user_id),
            contact_uuid_id = (select uuid_id from users where id = contact_id)
    """))

    # -- > update new columns to be non-nullable
    op.alter_column('contacts', 'user_uuid_id', nullable=False)
    op.alter_column('contacts', 'contact_uuid_id', nullable=False)

    # --> add new columns as nullable
    op.add_column('messages', sa.Column('user_from_uuid_id', sa.Uuid(), nullable=True))
    op.add_column('messages', sa.Column('user_to_uuid_id', sa.Uuid(), nullable=True))
    # --> update new columns with values from the users table

    conn.execute(sa.text("""
        update messages set 
            user_from_uuid_id = (select uuid_id from users where id = user_from_id), 
            user_to_uuid_id = (select uuid_id from users where id = user_to_id)
    """))
    # --> update new columns to be non-nullable
    op.alter_column('messages', 'user_from_uuid_id', nullable=False)
    op.alter_column('messages', 'user_to_uuid_id', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('messages', 'user_to_uuid_id')
    op.drop_column('messages', 'user_from_uuid_id')

    op.drop_column('contacts', 'contact_uuid_id')
    op.drop_column('contacts', 'user_uuid_id')
    # ### end Alembic commands ###