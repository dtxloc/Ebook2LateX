import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username_email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="Editor")
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    documents = relationship("Document", back_populates="owner")
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"))
    file_name = Column(Text, nullable=False)
    file_path_url = Column(Text, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="Pending")
    version = Column(Integer, nullable=False, default=1, server_default="1")

    owner = relationship("User", back_populates="documents")
    formulas = relationship(
        "FormulaEntry", back_populates="document", cascade="all, delete-orphan"
    )


class FormulaEntry(Base):
    __tablename__ = "formula_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    raw_image_path = Column(Text)
    latex_content = Column(Text)
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    document = relationship("Document", back_populates="formulas")
    logs = relationship("Log", back_populates="formula", cascade="all, delete-orphan")
    favorited_by = relationship(
        "UserFavorite", back_populates="formula", cascade="all, delete-orphan"
    )


class Log(Base):
    __tablename__ = "logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    formula_id = Column(UUID(as_uuid=True), ForeignKey("formula_entries.id", ondelete="CASCADE"))
    processing_time_ms = Column(Integer)
    confidence_score = Column(Numeric(3, 2))
    error_type = Column(String(100))
    error_message = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    environment_info = Column(JSONB)

    formula = relationship("FormulaEntry", back_populates="logs")


class UserFavorite(Base):
    __tablename__ = "user_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "formula_id", name="uq_user_favorites_user_formula"),
    )

    favorite_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    formula_id = Column(
        UUID(as_uuid=True),
        ForeignKey("formula_entries.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorites")
    formula = relationship("FormulaEntry", back_populates="favorited_by")
