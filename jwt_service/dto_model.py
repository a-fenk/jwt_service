from pydantic import BaseModel
from humps import camelize


class DTOModel(BaseModel):
    class Config:
        populate_by_name = True
        alias_generator = camelize
