from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class DTOModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True,
        alias_generator=to_camel,
    )
