from pydantic import BaseModel
from humps import camelize


class DTOModel(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        alias_generator = camelize
