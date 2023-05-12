from typing import List, Optional

from pydantic import BaseModel

from connect_transformations.models import Columns


class AdditionalValues(BaseModel):
    operation: Optional[str]
    value: Optional[str]


class Settings(BaseModel):
    from_: Optional[str]
    value: Optional[str]
    match_condition: Optional[bool]
    additional_values: Optional[List[AdditionalValues]]

    class Config:
        fields = {
            'from_': 'from',
        }


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
