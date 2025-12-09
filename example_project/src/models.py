"""Database models."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: int
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


@dataclass
class Task:
    id: int
    title: str
    description: str
    status: str  # 'todo', 'in_progress', 'done'
    priority: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
