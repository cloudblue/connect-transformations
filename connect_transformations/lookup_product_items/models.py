from typing import Optional

from pydantic import BaseModel

from connect_transformations.models import Columns


class Settings(BaseModel):
    product_id: Optional[str]
    product_column: Optional[str]
    lookup_type: Optional[str]
    from_: Optional[str]
    prefix: Optional[str]
    action_if_not_found: Optional[str]
    product_lookup_mode: Optional[str]

    class Config:
        fields = {
            'from_': 'from',
        }


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
