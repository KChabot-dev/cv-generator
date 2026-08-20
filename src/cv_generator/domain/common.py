from pydantic import BaseModel, Field


class PartialDate(BaseModel):
    year: int = Field(ge=1)
    month: int | None = Field(default=None, ge=1, le=12)

def is_definitely_before(first: PartialDate, second: PartialDate) -> bool:
    if first.year < second.year:
        return True

    if (
        first.year == second.year
        and first.month is not None
        and second.month is not None
        and first.month < second.month
    ):
        return True

    return False