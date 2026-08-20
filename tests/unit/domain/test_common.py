import pytest
from pydantic import ValidationError

from cv_generator.domain.common import PartialDate


def test_partial_date_accepts_valid_year_and_month() -> None:
    value = PartialDate(year=2026, month=8)

    assert value.year == 2026
    assert value.month == 8


@pytest.mark.parametrize("month", [0, 13])
def test_partial_date_rejects_invalid_month(month: int) -> None:
    with pytest.raises(ValidationError):
        PartialDate(year=2026, month=month)


def test_partial_date_accepts_year_without_month() -> None:
    value = PartialDate(year=2014)

    assert value.year == 2014
    assert value.month is None