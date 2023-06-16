from typing import Optional

from pydantic import BaseModel

from connect_transformations.models import Columns


class Settings(BaseModel):
    from_: Optional[str]
    to: Optional[str]
    action_if_not_found: Optional[str]

    class Config:
        fields = {
            'from_': 'from',
        }


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
