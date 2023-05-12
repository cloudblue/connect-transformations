from typing import List, Optional

from pydantic import BaseModel


class Error(BaseModel):
    error: str


class ValidationResult(BaseModel):
    overview: str


class StreamsColumn(BaseModel):
    id: Optional[str]
    name: Optional[str]
    nullable: Optional[bool]
    type: Optional[str]
    output: Optional[bool]
    position: Optional[int]
    required: Optional[bool]


class Mapping(BaseModel):
    from_: Optional[str]
    to: Optional[str]

    class Config:
        fields = {
            'from_': 'from',
        }


class Columns(BaseModel):
    input: Optional[List[StreamsColumn]]
    output: Optional[List[StreamsColumn]]
