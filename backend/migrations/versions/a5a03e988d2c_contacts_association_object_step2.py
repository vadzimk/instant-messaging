"""contacts_association_object_step2

Revision ID: a5a03e988d2c
Revises: dbf72c3d5910
Create Date: 2024-10-31 17:49:15.864751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5a03e988d2c'
down_revision: Union[str, None] = 'dbf72c3d5910'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contacts')
    op.rename_table('contacts1', 'contacts')
    # Retrieve the names of old foreign key constraints for `contacts` from information_schema
    conn = op.get_bind()
    old_fk_constraints = conn.execute(sa.text("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'contacts' 
              AND constraint_type = 'FOREIGN KEY';
        """)).fetchall()
    # Drop old foreign key constraints on `contacts`
    for constraint in old_fk_constraints:
        op.drop_constraint(constraint[0], 'contacts', type_='foreignkey', schema='public')

    # Recreate foreign key constraints on the new `contacts` table with old names
    op.create_foreign_key('fk_contacts_user_id_users', 'contacts', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_contacts_contact_id_users', 'contacts', 'users', ['contact_id'], ['id'],
                          ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_contacts_user_id_users', 'contacts', type_='foreignkey', schema='public')
    op.drop_constraint('fk_contacts_contact_id_users', 'contacts', type_='foreignkey', schema='public')

    op.rename_table('contacts', 'contacts1')
    # Recreate the old foreign key constraints for the `contacts1` table
    op.create_foreign_key('fk_contacts1_user_id_users', 'contacts1', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_contacts1_contact_id_users', 'contacts1', 'users', ['contact_id'], ['id'],
                          ondelete='CASCADE')

    op.create_table('contacts',
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('contact_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['contact_id'], ['users.id'], name='fk_contacts_contact_id_users', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_contacts_user_id_users', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'contact_id', name='contacts_pkey')
    )
    conn = op.get_bind()
    conn.execute(sa.text("""
        insert into contacts (user_id, contact_id)
        select user_id, contact_id 
        from contacts1
    """))
    # ### end Alembic commands ###
