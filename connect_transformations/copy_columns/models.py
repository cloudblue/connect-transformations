from typing import List, Optional

from pydantic import BaseModel

from connect_transformations.models import Columns, Mapping


class Configuration(BaseModel):
    settings: Optional[List[Mapping]]
    columns: Optional[Columns]
