from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CategoryCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Category name"
    )

    description: Optional[str] = Field(
        None,
        max_length=200,
        description="Category description"
    )


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50
    )

    description: Optional[str] = Field(
        None,
        max_length=200
    )


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TodoCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Todo title"
    )

    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Todo description"
    )

    category_id: int = Field(
        ...,
        gt=0,
        description="Category ID"
    )

    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Todo priority"
    )

    due_date: Optional[datetime] = Field(
        None,
        description="Todo due date and time"
    )


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100
    )

    description: Optional[str] = Field(
        None,
        max_length=500
    )

    category_id: Optional[int] = Field(
        None,
        gt=0
    )

    completed: Optional[bool] = None

    priority: Optional[Priority] = None

    due_date: Optional[datetime] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None

    category_id: int
    category_name: str

    completed: bool

    priority: Priority

    due_date: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TodoListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    todos: list[TodoResponse]
