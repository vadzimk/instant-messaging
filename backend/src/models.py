from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy import MetaData, event, inspect, String, Boolean, Text, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, WriteOnlyMapped


class Model(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",  # naming of indexes
        "uq": "uq_%(table_name)s_%(column_0_name)s",  # naming of unique constraints
        "ck": "ck_%(table_name)s_%(constraint_name)s",  # naming of check constraints
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # naming of foreign key constraints
        "pk": "pk_%(table_name)s",  # naming of primary key constraints
    })


# join table at level sqlalchemy_core
# https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#self-referential-many-to-many
Contact = Table('contacts',
                Model.metadata,
                Column('user_id', PSQL_UUID, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True,
                       nullable=False),
                Column('contact_id', PSQL_UUID, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True,
                       nullable=False),
                )


class User(Model):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    first_name: Mapped[str] = mapped_column(String(64), index=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    messages_sent: WriteOnlyMapped[list['Message']] = relationship(
        back_populates='user_from',
        foreign_keys='Message.user_from_id',
        cascade='all, delete-orphan',
        passive_deletes=True)
    messages_received: WriteOnlyMapped[list['Message']] = relationship(
        back_populates='user_to',
        foreign_keys='Message.user_to_id',
        cascade='all, delete-orphan',
        passive_deletes=True)
    # many-to-many managed by sqlalchemy relationship
    contacts: Mapped[list['User']] = relationship(
        'User',
        back_populates='contacts_of',
        lazy='selectin',
        secondary='contacts',
        primaryjoin='User.id == contacts.c.user_id',
        # Contact.c provides access to the column definitions of the table.
        secondaryjoin='User.id == contacts.c.contact_id',
    )
    contacts_of: Mapped[list['User']] = relationship(
        'User',
        back_populates='contacts',
        lazy='selectin',
        secondary='contacts',
        primaryjoin='User.id == contacts.c.contact_id',
        secondaryjoin='User.id == contacts.c.user_id',
    )

    def __repr__(self):
        return f'User({self.id}, "{self.email}")'

    def dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_active': self.is_active,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }


# one-on-one chat
# storing in rdbms only for demo purposes, such data should be stored in key-value store such as Cassandra
class Message(Model):
    __tablename__ = 'messages'
    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)

    user_from_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user_to_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    user_from: Mapped['User'] = relationship(lazy='joined', back_populates='messages_sent', innerjoin=True,
                                             foreign_keys=[user_from_id])
    user_to: Mapped['User'] = relationship(lazy='joined', back_populates='messages_received', innerjoin=True,
                                           foreign_keys=[user_to_id])

    def __repr__(self):
        return (f'Message({self.id}, '
                f'user_from_id={self.user_from_id}, '
                f'user_to_id={self.user_to_id}, '
                f'content={self.content})')

    def dict(self):
        return {
            'id': self.id,
            'user_from_id': self.user_from_id,
            'user_to_id': self.user_to_id,
            'content': self.content,
            'created_at': self.created_at,
        }


# ==================================== BOTTOM OF FILE =====================================================
# this avoids lazy loading of relationships after the session is flushed, needed for asynchronous sqlalchemy
@event.listens_for(Model, 'init', propagate=True)
def init_relationships(tgt, arg, kw):
    mapper = inspect(tgt.__class__)
    for arg in mapper.relationships:
        if arg.collection_class is None and arg.uselist:
            continue  # skip write-only and similar relationships
        if arg.key not in kw:
            kw.setdefault(
                arg.key, None if not arg.uselist else arg.collection_class())
