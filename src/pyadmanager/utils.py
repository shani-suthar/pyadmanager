"""Helpers for building GAM REST resource paths.

GAM REST resources are addressed by path, e.g. `networks/{code}/lineItems/{id}`.
These helpers build that path from a network code, a `gam_obj_type` (the plural
REST resource name, e.g. `"lineItems"`), and optionally a numeric id. The same
paths are used both as GET endpoints (`gam_obj_id_path`) and as the string
values compared against in id-based filter clauses (see `filters.GAMRestFilters.id_based_filter`).
"""

from typing import overload


def gam_obj_path(network_code: str, gam_obj_type: str) -> str:
    """Build the collection-level REST path for `gam_obj_type` (e.g. `networks/123/lineItems`).

    Used as the base endpoint for list/create requests, as opposed to
    `gam_obj_id_path`, which addresses a single resource within it.
    """
    return f"networks/{network_code}/{gam_obj_type}"


@overload
def gam_obj_id_path(ids: int, network_code: str, gam_obj_type: str) -> str: ...


@overload
def gam_obj_id_path(ids: list[int], network_code: str, gam_obj_type: str) -> list[str]: ...


@overload
def gam_obj_id_path(ids: None, network_code: str, gam_obj_type: str) -> None: ...


def gam_obj_id_path(
    ids: int | list[int] | None, network_code: str, gam_obj_type: str
) -> str | list[str] | None:
    """Resolve one or more resource ids to their full GAM REST path(s).

    Overloaded so callers get back the same shape they passed in: a single
    `int` id resolves to one path `str`, a `list[int]` resolves to a
    `list[str]` (one path per id, same order), and `None` passes through as
    `None` (meaning "no id filter requested"). Filter builders rely on this
    to turn a caller-supplied `line_item_id=[1, 2]` into the resource paths
    that `GAMRestFilters.id_based_filter` then quotes into an `OR` clause.
    """
    if ids is None:
        return None

    if isinstance(ids, int):
        return f"{gam_obj_path(network_code, gam_obj_type)}/{ids}"

    if isinstance(ids, list):
        vals = [f"{gam_obj_path(network_code, gam_obj_type)}/{i}" for i in ids]
        return vals
