from typing import Dict, Optional

from pydantic import BaseModel

from connect_transformations.models import Columns


class CapturingGroup(BaseModel):
    name: str
    type: str


class CapturingGroups(BaseModel):
    groups: Dict[str, CapturingGroup]


class RegexData(BaseModel):
    pattern: Optional[str]
    groups: Optional[Dict]


class Settings(BaseModel):
    from_: Optional[str]
    regex: Optional[RegexData]

    class Config:
        fields = {
            'from_': 'from',
        }


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
