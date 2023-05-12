from typing import Optional

from pydantic import BaseModel

from connect_transformations.models import Columns


class Currency(BaseModel):
    code: str
    description: str


class CurrencyColumn(BaseModel):
    column: Optional[str]
    currency: Optional[str]


class Settings(BaseModel):
    from_: Optional[CurrencyColumn]
    to: Optional[CurrencyColumn]

    class Config:
        fields = {
            'from_': 'from',
        }


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
