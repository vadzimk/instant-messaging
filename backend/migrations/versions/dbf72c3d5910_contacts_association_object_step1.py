"""contacts level orm step1

Revision ID: dbf72c3d5910
Revises: f18bda8d1da3
Create Date: 2024-10-31 14:51:33.306887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbf72c3d5910'
down_revision: Union[str, None] = 'f18bda8d1da3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Create the uuid-ossp extension if it doesn't exist
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")  # <-- for the server_default function to work

    op.create_table('contacts1',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('contact_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['contact_id'], ['users.id'], name=op.f('fk_contacts1_contact_id_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_contacts1_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_contacts1')),
    sa.UniqueConstraint('user_id', 'contact_id', name='_user_contact_uc')
    )
    conn = op.get_bind()
    conn.execute(sa.text("""
        insert into contacts1 (id, user_id, contact_id, created_at)
        select gen_random_uuid(), user_id, contact_id, NOW()
        from contacts
    """))
    op.create_index(op.f('ix_contacts1_created_at'), 'contacts1', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contacts1_created_at'), table_name='contacts1')
    op.drop_table('contacts1')
    # ### end Alembic commands ###
