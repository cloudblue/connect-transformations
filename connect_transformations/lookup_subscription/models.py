from typing import Optional

from pydantic import BaseModel

from connect_transformations.models import Columns


class SubscriptionParameter(BaseModel):
    id: str
    name: str


class Parameter(BaseModel):
    id: Optional[str]
    name: Optional[str]


class Settings(BaseModel):
    lookup_type: Optional[str]
    from_: Optional[str]
    prefix: Optional[str]
    action_if_not_found: Optional[str]
    action_if_multiple: Optional[str]
    parameter: Optional[Parameter]

    class Config:
        fields = {
            'from_': 'from',
        }


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
