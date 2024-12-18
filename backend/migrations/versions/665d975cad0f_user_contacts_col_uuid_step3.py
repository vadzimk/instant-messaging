"""user contacts col uuid, step3

Revision ID: 665d975cad0f
Revises: a16e9c37fb11
Create Date: 2024-10-26 20:47:52.933080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '665d975cad0f'
down_revision: Union[str, None] = 'a16e9c37fb11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()  # <-- new

    # change contacts table pk
    contacts_pk_name = conn.execute(  # <-- new
        sa.text("""select constraint_name from information_schema.table_constraints 
        where table_name = 'contacts' and constraint_type = 'PRIMARY KEY';""")).scalar()

    op.drop_constraint(contacts_pk_name, 'contacts', type_='primary')  # <-- new

    op.create_primary_key('contacts_pkey', 'contacts', ['user_uuid_id', 'contact_uuid_id'])

    op.create_unique_constraint('uq_users_uuid_id', 'users', ['uuid_id'])  # <-- required for it to become a fk
    op.drop_constraint('fk_contacts_contact_id_users', 'contacts', type_='foreignkey')
    op.drop_constraint('fk_contacts_user_id_users', 'contacts', type_='foreignkey')
    op.create_foreign_key(op.f('fk_contacts_user_uuid_id_users'), 'contacts', 'users', ['user_uuid_id'], ['uuid_id'],
                          ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_contacts_contact_uuid_id_users'), 'contacts', 'users', ['contact_uuid_id'],
                          ['uuid_id'], ondelete='CASCADE')

    # change messages table pk
    messages_pk_name = conn.execute(  # <-- new
        sa.text("""select constraint_name from information_schema.table_constraints 
        where table_name = 'messages' and constraint_type = 'PRIMARY KEY';""")).scalar()

    op.drop_constraint(messages_pk_name, 'messages', type_='primary')  # <-- new
    op.create_primary_key('messages_pkey', 'messages', ['uuid_id'])

    op.drop_constraint('fk_messages_user_to_id_users', 'messages', type_='foreignkey')
    op.drop_constraint('fk_messages_user_from_id_users', 'messages', type_='foreignkey')
    op.create_foreign_key(op.f('fk_messages_user_from_uuid_id_users'), 'messages', 'users', ['user_from_uuid_id'],
                          ['uuid_id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_messages_user_to_uuid_id_users'), 'messages', 'users', ['user_to_uuid_id'],
                          ['uuid_id'], ondelete='CASCADE')

    # change users table pk
    users_pk_name = conn.execute(  # <-- new
        sa.text("""select constraint_name from information_schema.table_constraints 
        where table_name = 'users' and constraint_type = 'PRIMARY KEY';""")).scalar()
    op.drop_constraint(users_pk_name, 'users', type_='primary')  # <-- new

    op.create_primary_key('users_pkey', 'users', ['uuid_id'])  # <-- new

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()  # Get the connection

    # Revert changes in the users table
    op.drop_constraint('users_pkey', 'users', type_='primary')  # Drop the new primary key
    op.create_primary_key('users_old_pkey', 'users', ['id'])  # Assuming 'id' was the old primary key column

    # Revert changes in the messages table
    op.drop_constraint('messages_pkey', 'messages', type_='primary')  # Drop the new primary key
    op.create_primary_key('messages_old_pkey', 'messages', ['id'])  # Assuming 'id' was the old primary key column

    op.drop_constraint('fk_messages_user_from_uuid_id_users', 'messages', type_='foreignkey')
    op.drop_constraint('fk_messages_user_to_uuid_id_users', 'messages', type_='foreignkey')
    op.create_foreign_key('fk_messages_user_from_id_users', 'messages', 'users', ['user_from_uuid_id'], ['id'], ondelete='CASCADE')  # Reverting foreign key
    op.create_foreign_key('fk_messages_user_to_id_users', 'messages', 'users', ['user_to_uuid_id'], ['id'], ondelete='CASCADE')  # Reverting foreign key

    # Revert changes in the contacts table
    op.drop_constraint('contacts_pkey', 'contacts', type_='primary')  # Drop the new primary key
    op.create_primary_key('contacts_old_pkey', 'contacts', ['id'])  # Assuming 'id' was the old primary key column

    op.drop_constraint('fk_contacts_user_uuid_id_users', 'contacts', type_='foreignkey')
    op.drop_constraint('fk_contacts_contact_uuid_id_users', 'contacts', type_='foreignkey')
    op.create_foreign_key('fk_contacts_user_id_users', 'contacts', 'users', ['user_uuid_id'], ['id'], ondelete='CASCADE')  # Reverting foreign key
    op.create_foreign_key('fk_contacts_contact_id_users', 'contacts', 'users', ['contact_uuid_id'], ['id'], ondelete='CASCADE')  # Reverting foreign key

    # Drop unique constraint added in upgrade
    op.drop_constraint('uq_users_uuid_id', 'users', type_='unique')  # Drop unique constraint


