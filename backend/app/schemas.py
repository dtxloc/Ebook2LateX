from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username_email: str = Field(..., min_length=3, max_length=255)
    full_name: str | None = Field(default=None, max_length=100)
    role: str = Field(default="Editor", max_length=20)
    is_active: bool = True


class UserCreate(UserBase):
    password_hash: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    username_email: str | None = Field(default=None, min_length=3, max_length=255)
    password_hash: str | None = None
    full_name: str | None = Field(default=None, max_length=100)
    role: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None
    last_login: datetime | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    last_login: datetime | None = None
    created_at: datetime | None = None


class DocumentBase(BaseModel):
    user_id: UUID | None = None
    file_name: str
    file_path_url: str
    status: str = Field(default="Pending", max_length=50)
    version: int = 1


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    user_id: UUID | None = None
    file_name: str | None = None
    file_path_url: str | None = None
    status: str | None = Field(default=None, max_length=50)
    version: int | None = None


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    upload_date: datetime | None = None


class FormulaEntryBase(BaseModel):
    document_id: UUID
    raw_image_path: str | None = None
    latex_content: str | None = None
    order_index: int


class FormulaEntryCreate(FormulaEntryBase):
    pass


class FormulaEntryUpdate(BaseModel):
    document_id: UUID | None = None
    raw_image_path: str | None = None
    latex_content: str | None = None
    order_index: int | None = None


class FormulaEntryRead(FormulaEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LogBase(BaseModel):
    formula_id: UUID | None = None
    processing_time_ms: int | None = None
    confidence_score: Decimal | float | None = None
    error_type: str | None = None
    error_message: str | None = None
    environment_info: dict | None = None


class LogCreate(LogBase):
    pass


class LogRead(LogBase):
    model_config = ConfigDict(from_attributes=True)

    log_id: UUID
    timestamp: datetime | None = None


class FavoriteCreate(BaseModel):
    user_id: UUID
    formula_id: UUID


class FavoriteRead(FavoriteCreate):
    model_config = ConfigDict(from_attributes=True)

    favorite_id: UUID
    created_at: datetime | None = None


class UserDocumentCountRead(BaseModel):
    username_email: str
    full_name: str | None = None
    document_count: int
