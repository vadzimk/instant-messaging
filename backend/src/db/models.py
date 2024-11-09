from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import MetaData, event, inspect, String, Boolean, Text, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, WriteOnlyMapped


class Model(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",  # naming of indexes
        "uq": "uq_%(table_name)s_%(column_0_name)s",  # naming of unique constraints
        "ck": "ck_%(table_name)s_%(constraint_name)s",  # naming of check constraints
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # naming of foreign key constraints
        "pk": "pk_%(table_name)s",  # naming of primary key constraints
    })


# association object
class Contact(Model):
    __tablename__ = 'contacts'
    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    contact_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    user: Mapped['User'] = relationship(
        'User',
        back_populates='contacts',
        foreign_keys=[user_id],
        lazy='joined',
        innerjoin=True
    )
    contact_user: Mapped['User'] = relationship(
        'User',
        back_populates='associated_with',
        foreign_keys=[contact_id],
        lazy='joined',
        innerjoin=True
    )

    __table_args__ = (UniqueConstraint('user_id', 'contact_id', name='_user_contact_uc'),)

    def __repr__(self):
        return f'Contact({self.id}, user_id={self.user_id}, contact_id={self.contact_id})'

    def dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'created_at': self.created_at,
        }


class User(Model):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    first_name: Mapped[str] = mapped_column(String(64), index=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    last_active_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    telegram_id: Mapped[Optional[int]] = mapped_column(Integer(), index=True)
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
    # many-to-many not managed by sqlalchemy relationship
    contacts: Mapped[list['Contact']] = relationship(
        'Contact',
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan',
        foreign_keys='Contact.user_id'
    )
    associated_with: Mapped[list['Contact1']] = relationship(
        'Contact',
        back_populates='contact_user',
        lazy='selectin',
        cascade='all, delete-orphan',
        foreign_keys='Contact.contact_id'
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
    user_from: Mapped['User'] = relationship(
        lazy='joined',
        back_populates='messages_sent',
        innerjoin=True,
        foreign_keys=[user_from_id]
    )
    user_to: Mapped['User'] = relationship(
        lazy='joined',
        back_populates='messages_received',
        innerjoin=True,
        foreign_keys=[user_to_id]
    )

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
