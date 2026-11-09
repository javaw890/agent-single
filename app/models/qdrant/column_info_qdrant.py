from typing_extensions import TypedDict


class ColumnInfoQdrant(TypedDict):
    id:str
    name:str
    description:str
    alias:list[str]
    role:str
    examples:list
    type:str
    table_id:str
