from typing import List, Optional

from pydantic import BaseModel

from connect_transformations.models import Columns, Mapping


class AirTableBase(BaseModel):
    id: str
    name: str


class AirTableColumn(BaseModel):
    id: str
    name: str
    type: str


class AirTableTable(BaseModel):
    id: str
    name: str
    columns: List[AirTableColumn]


class MapBy(BaseModel):
    input_column: Optional[str]
    airtable_column: Optional[str]


class Settings(BaseModel):
    api_key: Optional[str]
    base_id: Optional[str]
    table_id: Optional[str]
    map_by: MapBy
    mapping: List[Mapping]


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
