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
        """Build an equality clause for `field` against one or more resource-path strings.

        Used for id-based fields (e.g. `name`, `order`) where `value` is
        already a full GAM resource path like `networks/123/lineItems/456`
        (see `utils.gam_obj_id_path`), always double-quoted per the REST
        filter grammar's string-quoting rule. A `list` becomes a
        parenthesized `OR` clause; `None` means "no filter" and returns `""`
        so `get_filter_string` can drop it.
        """
        if value is None:
            return ""

        if isinstance(value, str):
            return f'{field} = "{value}"'

        if isinstance(value, list):
            vals = " OR ".join([f'{field} = "{v}"' for v in value])
            return f"({vals})"

        raise TypeError(f"unsupported value type for {field!r}: {type(value)!r}")

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
        """Build a text-comparison clause for `field` from a string, list, or filter-type tuple.

        A plain `str` (or `list[str]`, joined as an `OR` clause) defaults to
        an `EQUAL_TO` comparison. Pass a `(value, filter_type)` tuple to use
        `CONTAINS`/`STARTWITH`/`ENDWITH` (rendered as `"*val*"`/`"val*"`/`"*val"`
        wildcards) or `IS_NULL` (which ignores `value` and emits `field IS NULL`).
        `None` means "no filter" and returns `""`.
        """
        if value is None:
            return ""

        # Handle List (IN clause)
        if isinstance(value, list):
            vals = " OR ".join([f'{field} = "{v}"' for v in value])
            return f"({vals})"

        # Handle Tuple or Single String
        val, f_type = value if isinstance(value, tuple) else (value, "EQUAL_TO")

        if not isinstance(val, str):
            raise TypeError(f"unsupported value type for {field!r}: {type(val)!r}")

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
        """Build an equality clause for `field` against a bare (unquoted) boolean.

        Booleans must be unquoted per the REST filter grammar (`archived = true`,
        not `archived = "true"`), unlike string/id fields. `None` means "no
        filter" and returns `""`.
        """
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
        """Build a numeric-comparison clause for `field` against a bare (unquoted) number.

        A plain number (or `list[int]`, joined as an `OR` clause of equality
        checks) defaults to `EQUAL_TO`. Pass a `(value, NUMBER_FILTER_TYPE)`
        tuple for `!=`/`>=`/`<=`/`>`/`<` comparisons. Numbers are never
        quoted, per the REST filter grammar. `None` means "no filter" and
        returns `""`.
        """
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
        """Build an equality/inequality clause for `field` against a bare (unquoted) integer id.

        Unlike `id_based_filter` (which compares against a quoted resource
        *path* string), this is for fields that are themselves numeric ids
        compared directly, e.g. `EQUAL_TO`/`NOT_EQUAL_TO` via a
        `(value, ID_FILTER_TYPE)` tuple. `None` means "no filter" and
        returns `""`.
        """
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


def get_filter_string(filters: list[str]) -> str | None:
    """Join a list of `GAMRestFilters.*_filter` clauses with `AND` into one filter string.

    Empty clauses (from unset fields) are dropped first. Returns `None`
    (rather than `""`) when every field was unset, so callers can pass the
    result straight through as an optional `filter` query param without an
    extra `if` check.
    """
    clauses = [clause for clause in filters if clause]
    filter_str = " AND ".join(clauses)
    return filter_str if filter_str else None
