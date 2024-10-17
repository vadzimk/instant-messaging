from sqlalchemy import MetaData, event, inspect, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Model(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",  # naming of indexes
        "uq": "uq_%(table_name)s_%(column_0_name)s",  # naming of unique constraints
        "ck": "ck_%(table_name)s_%(constraint_name)s",  # naming of check constraints
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # naming of foreign key constraints
        "pk": "pk_%(table_name)s",  # naming of primary key constraints
    })


class User(Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f'User({self.id}, "{self.email}")'


# ==================================== BOTTOM OF FILE =====================================================
@event.listens_for(Model, 'init', propagate=True)
def init_relationships(tgt, arg, kw):
    mapper = inspect(tgt.__class__)
    for arg in mapper.relationships:
        if arg.collection_class is None and arg.uselist:
            continue  # skip write-only and similar relationships
        if arg.key not in kw:
            kw.setdefault(
                arg.key, None if not arg.uselist else arg.collection_class())
