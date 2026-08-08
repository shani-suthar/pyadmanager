"""High-level client for the Google Ad Manager REST API."""

from typing import overload


@overload
def gam_obj_id_path(ids: int, network_code: str, gam_obj_type: str) -> str: ...


@overload
def gam_obj_id_path(ids: list[int], network_code: str, gam_obj_type: str) -> list[str]: ...


@overload
def gam_obj_id_path(ids: None, network_code: str, gam_obj_type: str) -> None: ...


def gam_obj_id_path(
    ids: int | list[int] | None, network_code: str, gam_obj_type: str
) -> str | list[str] | None:
    if ids is None:
        return None

    if isinstance(ids, int):
        return f"networks/{network_code}/{gam_obj_type}/{ids}"

    if isinstance(ids, list):
        vals = [f"networks/{network_code}/{gam_obj_type}/{i}" for i in ids]
        return vals

    return None


def gam_obj_path(network_code: str, gam_obj_type: str) -> str:
    return f"networks/{network_code}/{gam_obj_type}"
