"""Generic REST filter-string builders for the Google Ad Manager API.

Reference:
    https://developers.google.com/ad-manager/api/beta/filters

"""

from datetime import UTC, datetime
from typing import Literal, TypeVar, overload

_StrT = TypeVar("_StrT", bound=str)
_IntT = TypeVar("_IntT", bound=int)

TEXT_FILTER_TYPE = Literal["EQUAL_TO", "CONTAINS", "STARTWITH", "ENDWITH", "IS_NULL"]
NUMBER_FILTER_TYPE = Literal["EQUAL_TO", "NOT_EQUAL_TO", "GT_EQ", "LT_EQ", "GT", "LT"]
DATETIME_FILTER_TYPE = Literal["EQUAL_TO", "NOT_EQUAL_TO", "GT_EQ", "LT_EQ", "GT", "LT"]
ID_FILTER_TYPE = Literal["EQUAL_TO", "NOT_EQUAL_TO"]


class GAMRestFilters:
    """Utility for building REST-compliant filter strings for Google Ad Manager."""

    Text_Filter_Tuple = tuple[str, TEXT_FILTER_TYPE]
    Number_Filter_Tuple = tuple[int | float, NUMBER_FILTER_TYPE]
    Datetime_Filter_Type = tuple[datetime, DATETIME_FILTER_TYPE]

    @overload
    @staticmethod
    def id_based_filter(
        field: str,
        value: str,
    ) -> str: ...

    @overload
    @staticmethod
    def id_based_filter(
        field: str,
        value: list[_StrT],
    ) -> str: ...

    @overload
    @staticmethod
    def id_based_filter(
        field: str,
        value: None,
    ) -> str: ...

    @staticmethod
    def id_based_filter(
        field: str,
        value: str | list[str] | None,
    ) -> str:
        if value is None:
            return ""

        if isinstance(value, str):
            return f'{field} = "{value}"'

        if isinstance(value, list):
            vals = " OR ".join([f'{field} = "{v}"' for v in value])
            return f"({vals})"

        return ""

    @overload
    @staticmethod
    def text_filter(field: str, value: str) -> str: ...

    @overload
    @staticmethod
    def text_filter(field: str, value: list[_StrT]) -> str: ...

    @overload
    @staticmethod
    def text_filter(field: str, value: Text_Filter_Tuple) -> str: ...

    @overload
    @staticmethod
    def text_filter(field: str, value: None) -> str: ...

    @staticmethod
    def text_filter(field: str, value: str | list[str] | Text_Filter_Tuple | None) -> str:
        if value is None:
            return ""

        # Handle List (IN clause)
        if isinstance(value, list):
            vals = " OR ".join([f'{field} = "{v}"' for v in value])
            return f"({vals})"

        # Handle Tuple or Single String
        val, f_type = value if isinstance(value, tuple) else (value, "EQUAL_TO")

        templates = {
            "EQUAL_TO": '{} = "{}"',
            "CONTAINS": '{} = "*{}*"',
            "STARTWITH": '{} = "{}*"',
            "ENDWITH": '{} = "*{}"',
            "IS_NULL": "{} IS NULL",
        }
        return templates[f_type].format(field, val)

    @staticmethod
    def boolean_filter(field: str, value: bool | None) -> str:
        if value is None:
            return ""

        return f"{field} = {str(value).lower()}"

    @overload
    @staticmethod
    def number_filter(field: str, value: float) -> str: ...

    @overload
    @staticmethod
    def number_filter(field: str, value: list[_IntT]) -> str: ...

    @overload
    @staticmethod
    def number_filter(field: str, value: Number_Filter_Tuple) -> str: ...

    @overload
    @staticmethod
    def number_filter(field: str, value: None) -> str: ...

    @staticmethod
    def number_filter(field: str, value: float | list[int] | Number_Filter_Tuple | None) -> str:
        if value is None:
            return ""

        if isinstance(value, list):
            vals = " OR ".join([f"{field} = {v}" for v in value])
            return f"({vals})"

        val, f_type = value if isinstance(value, tuple) else (value, "EQUAL_TO")

        ops = {
            "EQUAL_TO": "=",
            "NOT_EQUAL_TO": "!=",
            "GT_EQ": ">=",
            "LT_EQ": "<=",
            "GT": ">",
            "LT": "<",
        }
        return f"{field} {ops[f_type]} {val}"

    @staticmethod
    def id_filter(field: str, value: int | tuple[int, ID_FILTER_TYPE] | None) -> str:
        if value is None:
            return ""

        val, f_type = value if isinstance(value, tuple) else (value, "EQUAL_TO")

        ops = {
            "EQUAL_TO": "=",
            "NOT_EQUAL_TO": "!=",
        }

        return f"{field} {ops[f_type]} {val}"

    @staticmethod
    def _to_rfc3339(dt: datetime) -> str:
        """Converts datetime to the format required by GAM REST API."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.isoformat()

    @staticmethod
    def date_filter(
        field: str, value: datetime | tuple[datetime, DATETIME_FILTER_TYPE] | None
    ) -> str:
        """Handles REST date filtering with RFC 3339 strings."""
        if value is None:
            return ""

        dt_val, f_type = value if isinstance(value, tuple) else (value, "EQUAL_TO")
        formatted_dt = GAMRestFilters._to_rfc3339(dt_val)

        ops = {
            "EQUAL_TO": "=",
            "GT_EQ": ">=",
            "LT_EQ": "<=",
            "GT": ">",
            "LT": "<",
        }

        return f'{field} {ops[f_type]} "{formatted_dt}"'


class BaseRestFilter:
    """Engine to combine multiple filter components into a final REST query string."""

    def _build_filter_list(self) -> list[str]:
        raise NotImplementedError("_build_filter_list is not implemented!!")

    def get_filter_string(self) -> str | None:
        # Filter out empty strings from optional filters
        clauses = [c for c in self._build_filter_list() if c]
        filter_str = " AND ".join(clauses)
        return filter_str if filter_str else None
