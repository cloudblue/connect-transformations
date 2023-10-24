from typing import Dict, Optional

from pydantic import BaseModel

from connect_transformations.models import Columns


class SubscriptionParameter(BaseModel):
    id: str
    name: str


class Parameter(BaseModel):
    id: Optional[str]
    name: Optional[str]


class OutputConfig(BaseModel):
    attribute: Optional[str]
    parameter: Optional[str]


class Settings(BaseModel):
    asset_type: Optional[str]
    asset_column: Optional[str]
    parameter: Optional[Parameter]
    parameter_column: Optional[str]
    item: Optional[Parameter]
    item_column: Optional[str]
    action_if_not_found: Optional[str]
    action_if_multiple: Optional[str]
    output_config: Optional[Dict[str, OutputConfig]]


class Configuration(BaseModel):
    settings: Optional[Settings]
    columns: Optional[Columns]
