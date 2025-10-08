from pydantic import BaseModel, Field, ConfigDict

class Cat(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    color: str
    color_eye: str

    model_config = ConfigDict(from_attributes=True)

