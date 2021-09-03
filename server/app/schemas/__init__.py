import datetime

from pydantic import BaseModel
from uuid import UUID


class Base(BaseModel):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
