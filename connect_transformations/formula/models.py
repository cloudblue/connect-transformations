from typing import List, Optional

from pydantic import BaseModel, Field

from connect_transformations.models import Columns


class Stream(BaseModel):
    id: str
    type: str
    context: Optional[dict] = Field(default_factory=dict)


class Expression(BaseModel):
    to: Optional[str]
    formula: Optional[str]
    ignore_errors: Optional[bool]
    type: Optional[str]
    precision: Optional[int]


class Settings(BaseModel):
    expressions: Optional[List[Expression]]


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
    stream: Optional[Stream]
