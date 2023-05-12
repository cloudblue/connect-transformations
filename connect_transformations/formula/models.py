from typing import List, Optional

from pydantic import BaseModel

from connect_transformations.models import Columns


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
