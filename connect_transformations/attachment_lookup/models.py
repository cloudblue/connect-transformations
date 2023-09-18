from typing import List, Optional

from pydantic import BaseModel

from connect_transformations.models import Columns, Mapping


class StreamAttachment(BaseModel):
    id: str
    name: str
    file: str


class MapBy(BaseModel):
    input_column: Optional[str]
    attachment_column: Optional[str]


class Settings(BaseModel):
    file: Optional[str]
    sheet: Optional[str]
    map_by: List[MapBy]
    mapping: List[Mapping]


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
