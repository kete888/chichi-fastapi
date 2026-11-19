from pydantic import BaseModel

from schemas.chichi import ChichiOut


class SolarTermBrief(BaseModel):
    name: str
    date: str
    season: str
    foods: list[str]


class SolarTermOut(SolarTermBrief):
    dishes: list[ChichiOut]
