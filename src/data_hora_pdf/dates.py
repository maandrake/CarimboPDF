"""Date validation shared by the graphical and command-line interfaces."""

from datetime import date, datetime


def parse_date(value: str | None) -> date:
    if not value:
        return date.today()
    try:
        result = datetime.strptime(value, "%d/%m/%Y").date()
    except ValueError as exc:
        raise ValueError("Data inválida. Use DD/MM/AAAA.") from exc
    if result > date.today():
        raise ValueError("A data não pode ser futura.")
    return result
