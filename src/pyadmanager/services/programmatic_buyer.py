"""Filter builder for the ProgrammaticBuyers GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.programmaticBuyers
"""

from ..filters import BaseRestFilter, GAMRestFilters
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path


class ProgrammaticBuyerFilter(BaseRestFilter):
    """Filter for `ProgrammaticBuyerClient.list_programmatic_buyers`.

    One field per `programmaticBuyers` REST filter field.
    """

    def __init__(
        self,
        name: str | list[str] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        parent_account_id: str | list[str] | None = None,
        partner_client_id: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        agency: bool | None = None,
        preferred_deals_enabled: bool | None = None,
        programmatic_guaranteed_enabled: bool | None = None,
    ):
        """Store filter field values.

        `name`/`parent_account_id` are expected to already be full resource
        paths — `ProgrammaticBuyerClient.list_programmatic_buyers` resolves
        bare `buyer_account_id`/`parent_account_id` ints to them (both
        against the `programmaticBuyers` resource type, since a buyer's
        sponsor is itself a buyer) via `utils.gam_obj_id_path` before
        constructing this filter.
        """
        self.name = name
        self.display_name = display_name
        self.parent_account_id = parent_account_id
        self.partner_client_id = partner_client_id
        self.agency = agency
        self.preferred_deals_enabled = preferred_deals_enabled
        self.programmatic_guaranteed_enabled = programmatic_guaranteed_enabled

    def _build_filter_list(self) -> list[str]:
        return [
            GAMRestFilters.id_based_filter("name", self.name),
            GAMRestFilters.text_filter("displayName", self.display_name),
            GAMRestFilters.id_based_filter("parentAccountId", self.parent_account_id),
            GAMRestFilters.text_filter("partnerClientId", self.partner_client_id),
            GAMRestFilters.boolean_filter("agency", self.agency),
            GAMRestFilters.boolean_filter("preferredDealsEnabled", self.preferred_deals_enabled),
            GAMRestFilters.boolean_filter(
                "programmaticGuaranteedEnabled", self.programmatic_guaranteed_enabled
            ),
        ]


class ProgrammaticBuyerClient:
    """Client for the `programmaticBuyers` GAM REST resource."""

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "programmaticBuyers"

    def list_programmatic_buyers(
        self,
        buyer_account_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        parent_account_id: int | list[int] | None = None,
        partner_client_id: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        agency: bool | None = None,
        preferred_deals_enabled: bool | None = None,
        programmatic_guaranteed_enabled: bool | None = None,
        page_size: int = 1000,
    ):
        """List `programmaticBuyers`, paging through every result via `HTTPClient.fetch_all`.

        `buyer_account_id` resolves to `programmaticBuyers/{id}` path(s);
        `parent_account_id` resolves the same way (a buyer's sponsor is
        itself a buyer) — both via `utils.gam_obj_id_path` before filtering.
        Fields left as `None` are omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        buyer_account_id_str = gam_obj_id_path(
            buyer_account_id, self.network_code, self._gam_obj_type
        )
        parent_account_id_str = gam_obj_id_path(
            parent_account_id, self.network_code, self._gam_obj_type
        )

        filter_str = ProgrammaticBuyerFilter(
            name=buyer_account_id_str,
            display_name=display_name,
            parent_account_id=parent_account_id_str,
            partner_client_id=partner_client_id,
            agency=agency,
            preferred_deals_enabled=preferred_deals_enabled,
            programmatic_guaranteed_enabled=programmatic_guaranteed_enabled,
        ).get_filter_string()

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get_programmatic_buyer(self, buyer_account_id: int):
        """Fetch a single `programmaticBuyer` by numeric account id."""
        endpoint = gam_obj_id_path(buyer_account_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
